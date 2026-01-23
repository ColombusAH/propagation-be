"""
Mock-based tests for reader config endpoints (no DB required).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.db.dependencies import get_db
from app.main import app
from fastapi.testclient import TestClient
from tests.mock_utils import MockModel

client = TestClient(app)


class TestReaderConfigEndpointsMock:
    """Tests for reader configuration endpoints using mocks."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_list_readers(self):
        """Test listing all readers."""
        mock_db = MagicMock()
        readers = [
            MockModel(
                id="r1",
                name="Reader 1",
                ipAddress="192.168.1.10",
                type="UNKNOWN",
                status="ONLINE",
                storeId="store1",
            ),
            MockModel(
                id="r2",
                name="Reader 2",
                ipAddress="192.168.1.11",
                type="BATH",
                status="OFFLINE",
                storeId="store1",
            ),
        ]
        mock_db.rfidreader.find_many = AsyncMock(return_value=readers)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/readers/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["ip_address"] == "192.168.1.10"

    def test_get_reader_details(self):
        """Test getting a single reader."""
        mock_db = MagicMock()
        reader = MockModel(
            id="r1", name="Reader 1", ipAddress="1.1.1.1", type="GATE", status="ONLINE"
        )
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/readers/r1")
        assert response.status_code == 200
        assert response.json()["type"] == "GATE"

    def test_get_reader_not_found(self):
        """Test getting a non-existent reader."""
        mock_db = MagicMock()
        mock_db.rfidreader.find_unique = AsyncMock(return_value=None)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/readers/unknown")
        assert response.status_code == 404

    @patch("app.api.v1.endpoints.reader_config.generate_qr_code")
    @patch("app.api.v1.endpoints.reader_config.generate_bath_qr_data")
    def test_set_reader_as_bath(self, mock_gen_data, mock_gen_qr):
        """Test configuring reader as bath."""
        mock_gen_data.return_value = "BATH:123"
        mock_gen_qr.return_value = "data:image/png;base64,..."

        mock_db = MagicMock()

        # 1. Find existing
        reader = MockModel(id="r1", name="Reader 1", type="UNKNOWN")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        # 2. Update return
        updated_reader = MockModel(
            id="r1", name="Reader 1", type="BATH", qrCode="BATH:123"
        )
        mock_db.rfidreader.update = AsyncMock(return_value=updated_reader)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.put("/api/v1/readers/r1/set-bath", json={"name": "Bath 1"})
        assert response.status_code == 200
        data = response.json()
        assert data["qr_data"] == "BATH:123"
        assert data["qr_code"] == "data:image/png;base64,..."

        mock_db.rfidreader.update.assert_awaited_once()

    def test_set_reader_as_gate(self):
        """Test configuring reader as gate."""
        mock_db = MagicMock()

        reader = MockModel(id="r1", name="Reader 1", type="BATH")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        updated_reader = MockModel(id="r1", name="Reader 1", type="GATE", qrCode=None)
        mock_db.rfidreader.update = AsyncMock(return_value=updated_reader)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.put("/api/v1/readers/r1/set-gate")
        assert response.status_code == 200
        assert response.json()["message"] == "Reader configured as gate"

        mock_db.rfidreader.update.assert_awaited_once()

    @patch("app.api.v1.endpoints.reader_config.generate_qr_code")
    def test_get_reader_qr_success(self, mock_gen_qr):
        """Test getting QR for bath reader."""
        mock_gen_qr.return_value = "img"

        mock_db = MagicMock()
        reader = MockModel(id="r1", name="R1", type="BATH", qrCode="BATH:123")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/readers/r1/qr")
        assert response.status_code == 200
        assert response.json()["qr_data"] == "BATH:123"

    def test_get_reader_qr_wrong_type(self):
        """Test getting QR for non-bath reader."""
        mock_db = MagicMock()
        reader = MockModel(id="r1", type="GATE")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)

        app.dependency_overrides[get_db] = lambda: mock_db

        response = client.get("/api/v1/readers/r1/qr")
        assert response.status_code == 400
