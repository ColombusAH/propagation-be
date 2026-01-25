"""
Improved coverage tests for RFID Scan API endpoints.
Uses dependency overrides to bypass authentication and hit local logic.
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from prisma.models import User

from app.api.dependencies.auth import get_current_user as get_current_user_api
from app.core.deps import get_current_user as get_current_user_core
from app.core.permissions import requires_any_role
from app.main import app


# Create a mock user
def create_mock_user(role="SUPER_ADMIN"):
    return SimpleNamespace(
        id="user-1",
        email="admin@example.com",
        name="Admin User",
        phone="000-000-0000",
        address="Admin Addr",
        role=role,
        businessId="biz-1",
        darkMode=False,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
    )


@pytest.fixture
def auth_override():
    """Fixture to override auth dependencies."""
    mock_user = create_mock_user()
    app.dependency_overrides[get_current_user_core] = lambda: mock_user
    app.dependency_overrides[get_current_user_api] = lambda: mock_user
    # Mocking the factory is tricky, so we just let it run if get_current_user returns an admin
    yield
    app.dependency_overrides.clear()


class TestRfidScanCoverageV2:

    @pytest.mark.asyncio
    async def test_get_scan_status(self, client):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.is_connected = True
            mock_rfid.is_scanning = False
            mock_rfid.reader_ip = "127.0.0.1"
            mock_rfid.reader_port = 4001

            response = await client.get("/api/v1/rfid-scan/status")
            assert response.status_code == 200
            data = response.json()
            assert data["is_connected"] is True
            assert data["is_scanning"] is False

    @pytest.mark.asyncio
    async def test_connect_reader_success(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.is_connected = False
            mock_rfid.connect = AsyncMock(return_value=True)

            response = await client.post("/api/v1/rfid-scan/connect")
            assert response.status_code == 200
            assert response.json()["status"] == "connected"

    @pytest.mark.asyncio
    async def test_connect_reader_already_connected(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.is_connected = True

            response = await client.post("/api/v1/rfid-scan/connect")
            assert response.status_code == 200
            assert response.json()["status"] == "already_connected"

    @pytest.mark.asyncio
    async def test_connect_reader_fail(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.is_connected = False
            mock_rfid.connect = AsyncMock(return_value=False)

            response = await client.post("/api/v1/rfid-scan/connect")
            assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_disconnect_reader(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.disconnect = AsyncMock()

            response = await client.post("/api/v1/rfid-scan/disconnect")
            assert response.status_code == 200
            assert response.json()["status"] == "disconnected"

    @pytest.mark.asyncio
    async def test_start_scanning_passive_listener(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.tag_listener_service") as mock_listener,
        ):
            mock_listener._running = True
            mock_listener.start_scan = MagicMock(return_value=True)

            response = await client.post("/api/v1/rfid-scan/start")
            assert response.status_code == 200
            assert response.json()["mode"] == "passive_active_control"

    @pytest.mark.asyncio
    async def test_start_scanning_active_connect_needed(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.tag_listener_service") as mock_listener,
        ):
            mock_listener._running = False
            mock_rfid.is_connected = False
            mock_rfid.connect = AsyncMock(return_value=True)
            mock_rfid.start_scanning = AsyncMock()

            response = await client.post("/api/v1/rfid-scan/start")
            assert response.status_code == 200
            assert response.json()["mode"] == "active"

    @pytest.mark.asyncio
    async def test_start_scanning_active_connect_fail(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.tag_listener_service") as mock_listener,
        ):
            mock_listener._running = False
            mock_rfid.is_connected = False
            mock_rfid.connect = AsyncMock(return_value=False)

            response = await client.post("/api/v1/rfid-scan/start")
            assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_stop_scanning(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.tag_listener_service") as mock_listener,
        ):
            mock_listener._running = True
            mock_listener.stop_scan = MagicMock()
            mock_rfid.stop_scanning = AsyncMock()

            response = await client.post("/api/v1/rfid-scan/stop")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_perform_inventory_success(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.prisma_client") as mock_prisma,
        ):
            mock_rfid.is_connected = True
            mock_rfid.read_single_tag = AsyncMock(
                return_value=[{"epc": "E1", "rssi": -60}, {"epc": "E2", "rssi": -55}]
            )

            # Mock mapping found for E1, not for E2
            mock_prisma.client.tagmapping.find_unique = AsyncMock(
                side_effect=[MagicMock(encryptedQr="QR_E1"), None]
            )

            response = await client.post("/api/v1/rfid-scan/inventory")
            assert response.status_code == 200
            data = response.json()
            assert data["tag_count"] == 2
            assert data["tags"][0]["is_mapped"] is True
            assert data["tags"][0]["target_qr"] == "QR_E1"
            assert data["tags"][1]["is_mapped"] is False

    @pytest.mark.asyncio
    async def test_perform_inventory_mapping_error(self, client, auth_override):
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.prisma_client") as mock_prisma,
        ):
            mock_rfid.is_connected = True
            mock_rfid.read_single_tag = AsyncMock(return_value=[{"epc": "E1"}])
            mock_prisma.client.tagmapping.find_unique = AsyncMock(side_effect=Exception("DB Error"))

            response = await client.post("/api/v1/rfid-scan/inventory")
            assert response.status_code == 200
            # Should still return tag but with is_mapped=False due to catch-all
            assert response.json()["tags"][0]["is_mapped"] is False

    @pytest.mark.asyncio
    async def test_perform_inventory_fail(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.is_connected = True
            mock_rfid.read_single_tag = AsyncMock(side_effect=Exception("Hardware Error"))

            response = await client.post("/api/v1/rfid-scan/inventory")
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_initialize_device(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.initialize_device = AsyncMock(return_value=True)
            response = await client.post("/api/v1/rfid-scan/initialize")
            assert response.status_code == 200

            mock_rfid.initialize_device = AsyncMock(return_value=False)
            response = await client.post("/api/v1/rfid-scan/initialize")
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_set_power(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            # Invalid power
            response = await client.post("/api/v1/rfid-scan/power", json={"power_dbm": 35})
            assert response.status_code == 400

            # Valid power success
            mock_rfid.set_power = AsyncMock(return_value=True)
            response = await client.post("/api/v1/rfid-scan/power", json={"power_dbm": 25})
            assert response.status_code == 200

            # Valid power fail
            mock_rfid.set_power = AsyncMock(return_value=False)
            response = await client.post("/api/v1/rfid-scan/power", json={"power_dbm": 25})
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_read_tag_memory(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.read_tag_memory = AsyncMock(return_value=b"\xab\xcd")
            response = await client.post(
                "/api/v1/rfid-scan/read-memory",
                json={"mem_bank": 2, "start_addr": 0, "word_count": 6},
            )
            assert response.status_code == 200
            assert response.json()["data"] == "ABCD"

            mock_rfid.read_tag_memory = AsyncMock(return_value=None)
            response = await client.post(
                "/api/v1/rfid-scan/read-memory",
                json={"mem_bank": 2, "start_addr": 0, "word_count": 6},
            )
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_network_endpoints(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            # Get
            mock_rfid.get_network_config = AsyncMock(return_value={"ip": "1.1.1.1"})
            response = await client.get("/api/v1/rfid-scan/network")
            assert response.status_code == 200
            assert response.json()["ip"] == "1.1.1.1"

            # Set Success
            mock_rfid.set_network_config = AsyncMock(return_value=True)
            response = await client.post("/api/v1/rfid-scan/network", json={"ip": "1.1.1.2"})
            assert response.status_code == 200

            # Set Fail
            mock_rfid.set_network_config = AsyncMock(return_value=False)
            response = await client.post("/api/v1/rfid-scan/network", json={"ip": "1.1.1.2"})
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_rssi_filter(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.set_rssi_filter = AsyncMock(return_value=True)
            response = await client.post(
                "/api/v1/rfid-scan/rssi-filter", json={"antenna": 1, "threshold": 50}
            )
            assert response.status_code == 200

            mock_rfid.set_rssi_filter = AsyncMock(return_value=False)
            response = await client.post(
                "/api/v1/rfid-scan/rssi-filter", json={"antenna": 1, "threshold": 50}
            )
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_get_all_config(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.get_all_params = AsyncMock(return_value={"test": "val"})
            response = await client.get("/api/v1/rfid-scan/config")
            assert response.status_code == 200
            assert response.json()["test"] == "val"

    @pytest.mark.asyncio
    async def test_gpio_endpoints(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            # Get levels
            mock_rfid.get_gpio_levels = AsyncMock(return_value=[0, 1])
            response = await client.get("/api/v1/rfid-scan/gpio/levels")
            assert response.status_code == 200
            assert response.json()["gpio"] == [0, 1]

            # Set Success
            mock_rfid.set_gpio = AsyncMock(return_value=True)
            response = await client.post(
                "/api/v1/rfid-scan/gpio/config", json={"pin": 1, "direction": 1}
            )
            assert response.status_code == 200

            # Set Fail
            mock_rfid.set_gpio = AsyncMock(return_value=False)
            response = await client.post(
                "/api/v1/rfid-scan/gpio/config", json={"pin": 1, "direction": 1}
            )
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_relay_control(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            # Invalid relay
            response = await client.post("/api/v1/rfid-scan/relay/3", json={"close": True})
            assert response.status_code == 400

            # Valid Success
            mock_rfid.control_relay = AsyncMock(return_value=True)
            response = await client.post("/api/v1/rfid-scan/relay/1", json={"close": True})
            assert response.status_code == 200

            # Valid Fail
            mock_rfid.control_relay = AsyncMock(return_value=False)
            response = await client.post("/api/v1/rfid-scan/relay/1", json={"close": True})
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_gate_endpoints(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            # Get status
            mock_rfid.get_gate_status = AsyncMock(return_value={"gate": "ok"})
            response = await client.get("/api/v1/rfid-scan/gate/status")
            assert response.status_code == 200

            # Config Success
            mock_rfid.set_gate_config = AsyncMock(return_value=True)
            response = await client.post("/api/v1/rfid-scan/gate/config", json={"mode": 1})
            assert response.status_code == 200

            # Config Fail
            mock_rfid.set_gate_config = AsyncMock(return_value=False)
            response = await client.post("/api/v1/rfid-scan/gate/config", json={"mode": 1})
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_query_params(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.set_query_params = AsyncMock(return_value=True)
            response = await client.post("/api/v1/rfid-scan/query-params", json={"q_value": 4})
            assert response.status_code == 200

            mock_rfid.set_query_params = AsyncMock(return_value=False)
            response = await client.post("/api/v1/rfid-scan/query-params", json={"q_value": 4})
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_select_tag(self, client, auth_override):
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.select_tag = AsyncMock(return_value=True)
            response = await client.post("/api/v1/rfid-scan/select-tag", json={"epc_mask": "E1FF"})
            assert response.status_code == 200

            mock_rfid.select_tag = AsyncMock(return_value=False)
            response = await client.post("/api/v1/rfid-scan/select-tag", json={"epc_mask": "E1FF"})
            assert response.status_code == 500
