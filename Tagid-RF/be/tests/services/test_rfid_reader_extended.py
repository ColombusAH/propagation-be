"""
Extended tests for RFID Reader Service with Socket Mocking.
Refactored to use subclassing for mocking and unittest.mock.patch for robust interception.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.m200_protocol import M200Commands, M200Status
from app.services.rfid_reader import RFIDReaderService

# Explicitly mark this module for asyncio
pytestmark = pytest.mark.asyncio


class MockM200Response:
    """Mock response object mimicking M200Response structure."""

    def __init__(self, status=M200Status.SUCCESS, data=b"", cmd=0):
        self.status = status
        self.data = data
        self.cmd = cmd
        self.addr = 0
        self.crc = 0

    @property
    def success(self):
        # Allow both Enum vs Enum and value checks
        return self.status == M200Status.SUCCESS


class MockedRFIDReaderService(RFIDReaderService):
    """Subclass with mocked _send_command to return bytes."""

    def __init__(self):
        super().__init__()
        # Initialize internal state if needed
        self._socket = MagicMock()
        self.reader_ip = "127.0.0.1"
        self.reader_port = 4001
        self.is_connected = True  # Default to True for most tests

    def _send_command(self, command, max_retries=3):
        # Return dummy bytes that will be passed to M200ResponseParser.parse
        return b"DUMMY_BYTES"


async def test_connect_success():
    """Test successful connection."""
    service = MockedRFIDReaderService()
    service.is_connected = False  # Must be false to trigger connection logic

    with patch("socket.socket") as mock_sock_cls:
        mock_sock = MagicMock()
        mock_sock_cls.return_value = mock_sock

        # Override get_reader_info directly on the instance to return valid info
        service.get_reader_info = AsyncMock(
            return_value={"connected": True, "serial_number": "TEST"}
        )

        result = await service.connect()

        assert result is True
        assert service.is_connected is True
        mock_sock.connect.assert_called_once()


async def test_connect_failure():
    """Test connection failure."""
    service = MockedRFIDReaderService()
    service.is_connected = False

    with patch("socket.socket") as mock_sock_cls:
        mock_sock = MagicMock()
        mock_sock_cls.return_value = mock_sock
        mock_sock.connect.side_effect = Exception("Connection refused")

        result = await service.connect()

        assert result is False
        assert service.is_connected is False


async def test_disconnect():
    """Test disconnection."""
    service = MockedRFIDReaderService()
    service.is_connected = True

    # Inject mock socket
    mock_sock = MagicMock()
    service._socket = mock_sock

    await service.disconnect()

    assert service.is_connected is False
    assert service._socket is None
    # socket.close() called
    mock_sock.close.assert_called_once()


async def test_get_reader_info_success():
    """Test getting reader info."""
    service = MockedRFIDReaderService()
    service.is_connected = True

    mock_response = MockM200Response(
        status=M200Status.SUCCESS,
        data=b"\x00" * 152,
        cmd=M200Commands.RFM_GET_DEVICE_INFO,
    )

    with patch(
        "app.services.m200_protocol.M200ResponseParser.parse",
        return_value=mock_response,
    ):
        # We assume parse_device_info is called if success.
        with patch(
            "app.services.rfid_reader.parse_device_info",
            return_value={"mock": "data", "fw_version": "1.0"},
        ):

            info = await service.get_reader_info()

            # Check for error first
            assert "error" not in info, f"Got error: {info.get('error')}"

            assert info["mock"] == "data"
            assert info["connected"] is True


async def test_set_power_success():
    """Test setting power."""
    service = MockedRFIDReaderService()
    service.is_connected = True

    mock_response = MockM200Response(status=M200Status.SUCCESS)

    with patch(
        "app.services.m200_protocol.M200ResponseParser.parse",
        return_value=mock_response,
    ):
        result = await service.set_power(26)
        assert result is True


async def test_get_network_config():
    """Test getting network config."""
    service = MockedRFIDReaderService()
    service.is_connected = True

    mock_response = MockM200Response(status=M200Status.SUCCESS, data=b"net")

    with patch(
        "app.services.m200_protocol.M200ResponseParser.parse",
        return_value=mock_response,
    ):
        with patch(
            "app.services.rfid_reader.parse_network_response",
            return_value={"ip": "1.2.3.4"},
        ):

            config = await service.get_network_config()
            assert "error" not in config
            assert config["ip"] == "1.2.3.4"


async def test_read_single_tag_success():
    """Test reading single tag."""
    service = MockedRFIDReaderService()
    service.is_connected = True

    # Create mock response
    mock_response = MockM200Response(status=M200Status.SUCCESS, data=b"tag")

    with patch(
        "app.services.m200_protocol.M200ResponseParser.parse",
        return_value=mock_response,
    ):
        with patch(
            "app.services.rfid_reader.parse_inventory_response",
            return_value=[{"epc": "E200", "rssi": -50, "antenna_port": 1}],
        ):

            tags = await service.read_single_tag()

            assert len(tags) == 1
            assert tags[0]["epc"] == "E200"


async def test_initialize_device():
    """Test device initialization."""
    service = MockedRFIDReaderService()
    service.is_connected = True

    mock_response = MockM200Response(status=M200Status.SUCCESS)

    with patch(
        "app.services.m200_protocol.M200ResponseParser.parse",
        return_value=mock_response,
    ):
        result = await service.initialize_device()
        assert result is True
