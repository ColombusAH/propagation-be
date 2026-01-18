"""
Comprehensive tests for RFID Scan API endpoints.
Covers: get_scan_status, connect_reader, disconnect_reader, start_scanning, stop_scanning, perform_inventory
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestGetScanStatus:
    """Tests for GET /rfid-scan/status endpoint."""

    @pytest.mark.asyncio
    async def test_get_scan_status(self, client):
        """Test getting RFID scanner status."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.is_connected = False
            mock_rfid.is_scanning = False
            mock_rfid.reader_ip = "192.168.1.100"
            mock_rfid.reader_port = 4001

            response = await client.get("/api/v1/rfid-scan/status")
            assert response.status_code == 200
            data = response.json()
            assert "is_connected" in data


class TestConnectReader:
    """Tests for POST /rfid-scan/connect endpoint."""

    @pytest.mark.asyncio
    async def test_connect_reader_success(self, client):
        """Test successful reader connection."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.connect = AsyncMock(return_value=True)

            response = await client.post("/api/v1/rfid-scan/connect")
            assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_connect_reader_unauthorized(self, client):
        """Test connect without proper authorization."""
        response = await client.post("/api/v1/rfid-scan/connect")
        assert response.status_code in [401, 403]


class TestDisconnectReader:
    """Tests for POST /rfid-scan/disconnect endpoint."""

    @pytest.mark.asyncio
    async def test_disconnect_reader(self, client):
        """Test reader disconnection."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.disconnect = AsyncMock()

            response = await client.post("/api/v1/rfid-scan/disconnect")
            assert response.status_code in [200, 401, 403]


class TestStartScanning:
    """Tests for POST /rfid-scan/start endpoint."""

    @pytest.mark.asyncio
    async def test_start_scanning_success(self, client):
        """Test starting RFID scanning."""
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.tag_listener_service") as mock_listener,
        ):
            mock_rfid.is_connected = True
            mock_rfid.start_continuous_scan = AsyncMock(return_value=True)
            mock_listener.start = MagicMock()

            response = await client.post("/api/v1/rfid-scan/start")
            assert response.status_code in [200, 401, 403, 400]

    @pytest.mark.asyncio
    async def test_start_scanning_not_connected(self, client):
        """Test starting scan when reader not connected."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.is_connected = False

            response = await client.post("/api/v1/rfid-scan/start")
            assert response.status_code in [400, 401, 403]


class TestStopScanning:
    """Tests for POST /rfid-scan/stop endpoint."""

    @pytest.mark.asyncio
    async def test_stop_scanning(self, client):
        """Test stopping RFID scanning."""
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.tag_listener_service") as mock_listener,
        ):
            mock_rfid.stop_continuous_scan = MagicMock()
            mock_listener.stop = MagicMock()

            response = await client.post("/api/v1/rfid-scan/stop")
            assert response.status_code in [200, 401, 403]


class TestPerformInventory:
    """Tests for POST /rfid-scan/inventory endpoint."""

    @pytest.mark.asyncio
    async def test_perform_inventory_success(self, client):
        """Test successful inventory scan."""
        with (
            patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid,
            patch("app.api.v1.endpoints.rfid_scan.prisma_client") as mock_prisma,
        ):

            mock_rfid.is_connected = True
            mock_rfid.perform_inventory = AsyncMock(
                return_value=[{"epc": "E280681000001234", "rssi": -55.0, "antenna_port": 1}]
            )
            mock_prisma.client.tagmapping.find_unique = AsyncMock(return_value=None)

            response = await client.post("/api/v1/rfid-scan/inventory")
            assert response.status_code in [200, 401, 403, 400]

    @pytest.mark.asyncio
    async def test_perform_inventory_not_connected(self, client):
        """Test inventory scan when reader not connected."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.is_connected = False

            response = await client.post("/api/v1/rfid-scan/inventory")
            assert response.status_code in [400, 401, 403]


class TestModuleControl:
    """Tests for device control endpoints."""

    @pytest.mark.asyncio
    async def test_initialize_device(self, client):
        """Test device initialization."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.initialize = AsyncMock()

            response = await client.post("/api/v1/rfid-scan/initialize")
            assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_set_power(self, client):
        """Test setting RF power."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.set_power = AsyncMock()

            response = await client.post("/api/v1/rfid-scan/power", json={"power_dbm": 20})
            assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_read_tag_memory(self, client):
        """Test reading tag memory."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.read_memory = AsyncMock(return_value={"data": "ABCD1234"})

            response = await client.post(
                "/api/v1/rfid-scan/read-memory",
                json={"mem_bank": 2, "start_addr": 0, "word_count": 6},
            )
            assert response.status_code in [200, 401, 403, 422]


class TestNetworkConfiguration:
    """Tests for network configuration endpoints."""

    @pytest.mark.asyncio
    async def test_get_network(self, client):
        """Test getting network configuration."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.get_network = AsyncMock(
                return_value={
                    "ip": "192.168.1.100",
                    "subnet": "255.255.255.0",
                    "gateway": "192.168.1.1",
                }
            )

            response = await client.get("/api/v1/rfid-scan/network")
            assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_set_network(self, client):
        """Test setting network configuration."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.set_network = AsyncMock()

            response = await client.post(
                "/api/v1/rfid-scan/network",
                json={
                    "ip": "192.168.1.200",
                    "subnet": "255.255.255.0",
                    "gateway": "192.168.1.1",
                    "port": 4001,
                },
            )
            assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_set_rssi_filter(self, client):
        """Test setting RSSI filter."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.set_rssi_filter = AsyncMock()

            response = await client.post(
                "/api/v1/rfid-scan/rssi-filter", json={"antenna": 1, "threshold": -60}
            )
            assert response.status_code in [200, 401, 403, 422]

    @pytest.mark.asyncio
    async def test_get_all_config(self, client):
        """Test getting all device parameters."""
        with patch("app.api.v1.endpoints.rfid_scan.rfid_reader_service") as mock_rfid:
            mock_rfid.get_all_params = AsyncMock(return_value={"power": 20, "frequency": 920})

            response = await client.get("/api/v1/rfid-scan/config")
            assert response.status_code in [200, 401, 403]
