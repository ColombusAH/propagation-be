"""
Coverage tests for Inventory API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.main import app
from app.api import deps
from types import SimpleNamespace

# Create a mock user
def create_mock_user():
    from datetime import datetime
    return SimpleNamespace(
        id="user-1",
        email="test@example.com",
        name="Test User",
        phone="000-000-0000",
        address="Addr",
        role="CUSTOMER",
        businessId="b1",
        is_active=True,
        darkMode=False,
        createdAt=datetime.now()
    )

@pytest.fixture
def auth_override():
    """Fixture to override auth dependencies."""
    app.dependency_overrides[deps.get_current_active_user] = lambda: create_mock_user()
    yield
    app.dependency_overrides.clear()

class TestInventoryEndpointCoverage:

    @pytest.mark.asyncio
    async def test_create_inventory_snapshot_success(self, client, auth_override):
        with patch("app.api.v1.endpoints.inventory.inventory_service") as mock_service:
            mock_service.take_snapshot = AsyncMock(return_value="snap-123")
            
            payload = {
                "reader_id": "reader-1",
                "tags": [{"epc": "E1", "rssi": -60}, {"epc": "E2"}]
            }
            response = await client.post("/api/v1/inventory/snapshot", json=payload)
            assert response.status_code == 200
            assert response.json()["snapshot_id"] == "snap-123"
            assert response.json()["item_count"] == 2

    @pytest.mark.asyncio
    async def test_create_inventory_snapshot_fail(self, client, auth_override):
        with patch("app.api.v1.endpoints.inventory.inventory_service") as mock_service:
            mock_service.take_snapshot = AsyncMock(return_value=None)
            
            payload = {
                "reader_id": "reader-1",
                "tags": [{"epc": "E1"}]
            }
            response = await client.post("/api/v1/inventory/snapshot", json=payload)
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_get_current_stock(self, client, auth_override):
        with patch("app.api.v1.endpoints.inventory.inventory_service") as mock_service:
            mock_service.get_current_stock = AsyncMock(return_value={
                "totalItems": 10,
                "readerCount": 2,
                "readers": []
            })
            
            response = await client.get("/api/v1/inventory/stock?store_id=store-1")
            assert response.status_code == 200
            assert response.json()["totalItems"] == 10

    @pytest.mark.asyncio
    async def test_get_latest_snapshot_success(self, client, auth_override):
        with patch("app.api.v1.endpoints.inventory.inventory_service") as mock_service:
            mock_service.get_latest_snapshot = AsyncMock(return_value={"id": "s1", "tags": []})
            
            response = await client.get("/api/v1/inventory/snapshot/reader-1")
            assert response.status_code == 200
            assert response.json()["id"] == "s1"

    @pytest.mark.asyncio
    async def test_get_latest_snapshot_not_found(self, client, auth_override):
        with patch("app.api.v1.endpoints.inventory.inventory_service") as mock_service:
            mock_service.get_latest_snapshot = AsyncMock(return_value=None)
            
            response = await client.get("/api/v1/inventory/snapshot/reader-1")
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_inventory_history(self, client, auth_override):
        with patch("app.api.v1.endpoints.inventory.inventory_service") as mock_service:
            mock_service.get_inventory_history = AsyncMock(return_value=[{"id": "s1"}])
            
            response = await client.get("/api/v1/inventory/history/reader-1?limit=5")
            assert response.status_code == 200
            assert len(response.json()) == 1
