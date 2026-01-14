"""
Mocked tests for RFID Reader Service to achieve high code coverage.
Focuses on mocking socket communication and protocol handling.
"""

import asyncio
import socket
import struct
from unittest.mock import AsyncMock, MagicMock, PropertyMock, call, patch

import pytest

import app.services.rfid_reader as rfid_reader_module
from app.services.m200_protocol import M200Commands, M200Status
from app.services.rfid_reader import RFIDReaderService

# Mark all tests as async by default
pytestmark = pytest.mark.asyncio


class TestRFIDReaderServiceMocked:
    """Tests for RFIDReaderService with extensive mocking."""

    @pytest.fixture
    def service(self):
        """Fixture for RFIDReaderService."""
        return RFIDReaderService()

    @pytest.fixture
    def mock_socket(self):
        """Fixture for mocked socket."""
        mock = MagicMock()
        mock.recv.return_value = b""
        return mock

    async def test_connect_success_with_buffer_clear(self, service, mock_socket):
        """Test successful connection with buffer clearing."""
        with patch("socket.socket", return_value=mock_socket):
            mock_socket.recv.side_effect = [b"\x00\x00", BlockingIOError]
            with patch.object(
                service,
                "get_reader_info",
                return_value={"connected": True, "serial_number": "TEST1"},
            ):
                result = await service.connect()
                assert result is True

    async def test_connect_socket_error(self, service):
        """Test connection failure due to socket error."""
        with patch("socket.socket", side_effect=socket.error("Socket error")):
            result = await service.connect()
            assert result is False

    async def test_connect_timeout(self, service, mock_socket):
        """Test connection timeout."""
        with patch("socket.socket", return_value=mock_socket):
            mock_socket.connect.side_effect = socket.timeout
            result = await service.connect()
            assert result is False

    async def test_disconnect_with_scan_stop(self, service):
        """Test disconnect stops scanning."""
        service.is_connected = True
        service.is_scanning = True
        service._socket = MagicMock()

        async def dummy_scan():
            pass

        service._scan_task = asyncio.create_task(dummy_scan())

        with patch.object(service, "stop_scanning", new_callable=AsyncMock) as mock_stop:
            await service.disconnect()
            mock_stop.assert_awaited_once()

    async def test_send_command_success(self, service, mock_socket):
        """Test sending command and receiving valid response."""
        service.is_connected = True
        service._socket = mock_socket

        cmd = MagicMock()
        cmd.serialize.return_value = b"\xcf\x00\x00\x00\x00\x00\x00"
        cmd.cmd = 0x0102

        mock_socket.recv.side_effect = [
            b"\xcf",  # HEAD
            b"\x00\x01\x02\x00",  # Header
            b"\x00\x12\x34",  # Data + CRC
        ] + [b"\x00"] * 50

        with patch.object(rfid_reader_module.struct, "unpack", return_value=(0x0102,)):
            response = await asyncio.to_thread(service._send_command, cmd)
            assert response.startswith(b"\xcf")

    async def test_send_command_unsolicited_handling(self, service, mock_socket):
        """Test ignoring unsolicited messages."""
        service.is_connected = True
        service._socket = mock_socket

        cmd = MagicMock()
        cmd.serialize.return_value = b"CMD"
        cmd.cmd = 0xAAAA

        mock_socket.recv.side_effect = [
            b"\xcf",
            b"\x00\xbb\xbb\x00",
            b"\x00\x11",
            b"\xcf",
            b"\x00\xaa\xaa\x00",
            b"\x00\x22",
        ] + [b"\x00"] * 50

        with patch.object(rfid_reader_module.struct, "unpack", side_effect=[(0xBBBB,), (0xAAAA,)]):
            response = await asyncio.to_thread(service._send_command, cmd)
            assert len(response) > 0

    async def test_send_command_timeout(self, service, mock_socket):
        """Test timeout waiting for response."""
        service.is_connected = True
        service._socket = mock_socket

        cmd = MagicMock()
        cmd.serialize.return_value = b"CMD"
        cmd.cmd = 0xAAAA
        mock_socket.recv.side_effect = socket.timeout

        with pytest.raises(socket.timeout):
            await asyncio.to_thread(service._send_command, cmd)

    async def test_module_control_commands(self, service, mock_socket):
        """Test initialize and set power commands."""
        service.is_connected = True
        with patch.object(service, "_send_command", return_value=b"data"):
            # Patch name in module
            with patch.object(rfid_reader_module, "M200ResponseParser") as MockParser:
                MockParser.parse.return_value.success = True
                assert await service.initialize_device() is True
                assert await service.set_power(30) is True

    async def test_read_memory(self, service):
        """Test read_tag_memory."""
        service.is_connected = True
        with patch.object(service, "_send_command", return_value=b"data"):
            with patch.object(rfid_reader_module, "M200ResponseParser") as MockParser:
                MockParser.parse.return_value.success = True
                MockParser.parse.return_value.data = b"\x12\x34"
                result = await service.read_tag_memory(1, 0, 2)
                assert result == b"\x12\x34"

    async def test_network_config(self, service):
        """Test get/set network config."""
        service.is_connected = True

        with patch.object(service, "_send_command", return_value=b"data"):
            with patch.object(rfid_reader_module, "M200ResponseParser") as MockParser:
                MockParser.parse.return_value.success = True
                MockParser.parse.return_value.data = b"netdata"

                with patch.object(rfid_reader_module, "parse_network_response") as mock_net_parse:
                    mock_net_parse.return_value = {"ip": "1.2.3.4"}

                    result = await service.get_network_config()
                    assert result == {"ip": "1.2.3.4"}

                result = await service.set_network_config("1.2.3.4")
                assert result is True

    async def test_gpio_control(self, service):
        """Test GPIO operations."""
        service.is_connected = True

        with patch.object(service, "_send_command", return_value=b"data"):
            with patch.object(rfid_reader_module, "M200ResponseParser") as MockParser:
                MockParser.parse.return_value.success = True
                MockParser.parse.return_value.data = b"\x00"

                with patch.object(rfid_reader_module, "parse_gpio_levels", return_value={"in1": 1}):
                    result = await service.get_gpio_levels()
                    assert result is not None

                assert await service.set_gpio(1, 1, 1) is True

    async def test_relay_control(self, service):
        """Test relay control."""
        service.is_connected = True
        with patch.object(service, "_send_command", return_value=b"data"):
            with patch.object(rfid_reader_module, "M200ResponseParser") as MockParser:
                MockParser.parse.return_value.success = True
                assert await service.control_relay(1, True) is True

    async def test_scan_operations(self, service):
        """Test start and stop scanning."""
        service.is_connected = True
        service.is_scanning = False

        async def dummy_loop(cb=None):
            while service.is_scanning:
                await asyncio.sleep(0.01)

        service._scan_loop = dummy_loop
        await service.start_scanning()
        assert service.is_scanning is True
        scan_task = service._scan_task
        with patch.object(service, "_send_command"):
            await service.stop_scanning()
            assert service.is_scanning is False
            await asyncio.sleep(0.05)
            assert scan_task.done() or scan_task.cancelled()

    async def test_read_single_tag(self, service):
        """Test read_single_tag."""
        service.is_connected = True

        with patch.object(service, "_send_command", return_value=b"data"):

            # Mock the Parser class in the module
            with patch.object(rfid_reader_module, "M200ResponseParser") as MockParser:
                MockParser.parse.return_value.success = True
                MockParser.parse.return_value.status = 0  # OK
                MockParser.parse.return_value.data = b"tagdata"

                # Mock the parse function in the module
                with patch.object(rfid_reader_module, "parse_inventory_response") as mock_inv_parse:
                    mock_inv_parse.return_value = [{"epc": "E1", "rssi": -50, "antenna_port": 1}]

                    tags = await service.read_single_tag()
                    assert len(tags) == 1
                    assert tags[0]["epc"] == "E1"

                    # Test Empty case
                    MockParser.parse.return_value.status = M200Status.INVENTORY_COMPLETE
                    tags = await service.read_single_tag()
                    assert tags == []

    async def test_process_tag(self, service):
        """Test DB saving and broadcasting."""
        mock_db = MagicMock()
        mock_tag = MagicMock()
        mock_tag.id = 123
        mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

        # Patch SessionLocal in the module
        with (
            patch.object(rfid_reader_module, "SessionLocal", return_value=mock_db),
            patch.object(
                rfid_reader_module.manager, "broadcast", new_callable=AsyncMock
            ) as mock_broadcast,
        ):

            mock_actions = MagicMock()
            mock_actions.find_unique = AsyncMock(return_value=None)

            # Patch prisma_client instance in app.db.prisma (since it's imported in function)
            with patch("app.db.prisma.prisma_client") as mock_pc_instance:
                mock_pc_instance.client.tagmapping = mock_actions

                tag_data = {"epc": "E1", "rssi": -60, "antenna_port": 1, "timestamp": "now"}

                # Patch Models in module
                with (
                    patch.object(rfid_reader_module, "RFIDTag") as MockTag,
                    patch.object(rfid_reader_module, "RFIDScanHistory") as MockHist,
                ):

                    MockTag.return_value = MagicMock(id=999)

                    await service._process_tag(tag_data)

                    assert mock_db.commit.call_count >= 1
                    mock_broadcast.assert_awaited()
