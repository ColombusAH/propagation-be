from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.api.dependencies.auth import get_current_user as auth_get_user
from app.api.v1.endpoints.rfid_scan import router
from app.core.deps import get_current_user as core_get_user
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "admin_123"
    user.role = "SUPER_ADMIN"
    return user


@pytest.fixture
def test_app(mock_user):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[auth_get_user] = lambda: mock_user
    app.dependency_overrides[core_get_user] = lambda: mock_user
    return app


@pytest.fixture
async def client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_scan_status(client):
    with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_svc:
        mock_svc.is_connected = True
        mock_svc.is_scanning = False
        mock_svc.reader_ip = "1.1.1.1"
        mock_svc.reader_port = 4001
        response = await client.get("/rfid-scan/status")
        assert response.status_code == 200
        assert response.json()["is_connected"] is True


@pytest.mark.asyncio
async def test_connect_reader_success(client):
    with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_svc:
        mock_svc.is_connected = False
        mock_svc.connect = AsyncMock(return_value=True)
        response = await client.post("/rfid-scan/connect")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_start_scanning_passive(client):
    with patch("app.api.v1.endpoints.rfid_scan.tag_listener_service") as mock_tag_svc:
        mock_tag_svc._running = True
        mock_tag_svc.start_scan.return_value = True
        response = await client.post("/rfid-scan/start")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_perform_inventory_success(client):
    with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_svc:
        mock_svc.is_connected = True
        mock_svc.read_single_tag = AsyncMock(return_value=[{"epc": "E1", "rssi": -60}])
        # Patch at source since it is locally imported in the function
        with patch("app.db.prisma.prisma_client") as mock_p:
            mapping = MagicMock()
            mapping.encryptedQr = "QR1"
            mock_p.client.tagmapping.find_unique = AsyncMock(return_value=mapping)
            response = await client.post("/rfid-scan/inventory")
            assert response.status_code == 200
            assert response.json()["tag_count"] == 1


@pytest.mark.asyncio
async def test_set_power_success(client):
    with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_svc:
        mock_svc.set_power = AsyncMock(return_value=True)
        response = await client.post("/rfid-scan/power", json={"power_dbm": 25})
        assert response.status_code == 200
