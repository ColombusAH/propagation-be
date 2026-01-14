"""
Tests for Exit Scan Router - theft detection and tag status management.
"""
import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.main import app
from app.services.database import get_db
from app.models.rfid_tag import RFIDTag
from app.models.store import User, Store, Notification

# Mark as markers for easier selection
pytestmark = pytest.mark.asyncio

class TestExitScanRouter:
    """Comprehensive tests for exit_scan router."""

    @pytest.fixture
    def mock_db(self):
        """Fixture for a mocked database session."""
        db = MagicMock(spec=Session)
        mock_query = MagicMock()
        db.query.return_value = mock_query
        # Each filter returns the same mock_query to handle chains
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.first.return_value = None
        return db, mock_query

    @pytest.fixture
    def override_get_db(self, mock_db):
        """Override the database dependency."""
        app.dependency_overrides[get_db] = lambda: mock_db[0]
        yield
        app.dependency_overrides.pop(get_db, None)

    async def test_check_exit_scan_all_paid(self, client: AsyncClient, mock_db, override_get_db):
        """Test exit scan where all items are paid."""
        db, mock_query = mock_db
        # Setup mock tags
        tag1 = MagicMock(spec=RFIDTag)
        tag1.epc = "E1"
        tag1.is_paid = True
        
        tag2 = MagicMock(spec=RFIDTag)
        tag2.epc = "E2"
        tag2.is_paid = True

        # Sequential tag lookups
        mock_query.first.side_effect = [tag1, tag2]

        request_data = {
            "epcs": ["E1", "E2"],
            "gate_id": "main-exit"
        }

        response = await client.post("/api/v1/exit-scan/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_scanned"] == 2
        assert data["paid_count"] == 2
        assert data["unpaid_count"] == 0
        assert data["alert_sent"] is False

    async def test_check_exit_scan_unpaid_alert(self, client: AsyncClient, mock_db, override_get_db):
        """Test exit scan with unpaid items triggering alerts."""
        db, mock_query = mock_db
        
        # Setup mock tag
        tag1 = MagicMock(spec=RFIDTag)
        tag1.epc = "E_UNPAID"
        tag1.is_paid = False
        tag1.product_name = "Unpaid Product"
        tag1.product_sku = "SKU_UNPAID"
        tag1.price_cents = 5000
        
        # Setup stakeholder
        user1 = MagicMock(spec=User)
        user1.id = 1
        user1.name = "Manager One"
        user1.role = "MANAGER"
        user1.store_id = 1
        
        # Configure query chain
        # 1. tag lookup (first) -> tag1
        # 2. stakeholders lookup (all) -> [user1]
        # 3. store lookup (first) -> None
        # 4. preference lookup (first) -> None
        
        mock_query.all.return_value = [user1]
        mock_query.first.side_effect = [tag1, None, None]
        
        request_data = {
            "epcs": ["E_UNPAID"],
            "gate_id": "main-exit",
            "store_id": 1
        }

        response = await client.post("/api/v1/exit-scan/check", json=request_data)
        
        # Diagnostics if it still fails
        data = response.json()
        if data.get("alert_recipients") == 0:
             print(f"DEBUG: stakeholders query match failed. Count: {len(mock_query.all.return_value)}")
             
        assert response.status_code == 200
        assert data["unpaid_count"] == 1
        assert data["alert_sent"] is True
        assert data["alert_recipients"] == 1
        
        # Verify notification was added
        assert db.add.called
        assert db.commit.called

    async def test_check_exit_scan_unknown_tag(self, client: AsyncClient, mock_db, override_get_db):
        """Test exit scan with unknown EPC."""
        db, mock_query = mock_db
        mock_query.first.return_value = None
        mock_query.all.return_value = []

        request_data = {
            "epcs": ["UNKNOWN_EPC"]
        }

        response = await client.post("/api/v1/exit-scan/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["unpaid_count"] == 1
        assert data["unpaid_items"][0]["product_name"] == "מוצר לא מזוהה"

    async def test_mark_tags_as_paid(self, client: AsyncClient, mock_db, override_get_db):
        """Test marking tags as paid."""
        db, mock_query = mock_db
        tag = MagicMock(spec=RFIDTag)
        tag.epc = "E1"
        tag.is_paid = False
        
        mock_query.first.return_value = tag
        
        response = await client.post("/api/v1/exit-scan/mark-paid", json=["E1"])
        
        assert response.status_code == 200
        assert tag.is_paid is True
        assert tag.paid_at is not None
        assert db.commit.called

    async def test_mark_tags_as_unpaid(self, client: AsyncClient, mock_db, override_get_db):
        """Test marking tags as unpaid."""
        db, mock_query = mock_db
        tag = MagicMock(spec=RFIDTag)
        tag.epc = "E1"
        tag.is_paid = True
        
        mock_query.first.return_value = tag
        
        response = await client.post("/api/v1/exit-scan/mark-unpaid", json=["E1"])
        
        assert response.status_code == 200
        assert tag.is_paid is False
        assert tag.paid_at is None
        assert db.commit.called
