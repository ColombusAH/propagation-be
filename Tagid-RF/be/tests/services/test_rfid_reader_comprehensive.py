"""
Comprehensive tests for RFID Reader Service.
Covers connection, disconnection, command sending, scanning, and error handling.
"""
import pytest
import socket
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rfid_reader import RFIDReaderService, HEAD
from app.services.m200_protocol import M200Command, calculate_crc16
import struct


@pytest.fixture
def reader():
    """Create RFID Reader service instance."""
    service = RFIDReaderService()
    service.reader_ip = "192.168.1.100"
    service.reader_port = 4001
    return service


# --- Initialization Tests ---
def test_reader_initialization(reader):
    """Test reader initializes with correct defaults."""
    assert reader.is_connected is False
    assert reader.is_scanning is False
    assert reader._socket is None


def test_get_status(reader):
    """Test get_status returns correct state."""
    status = reader.get_status()
    assert status["is_connected"] is False
    assert status["is_scanning"] is False
    assert status["reader_ip"] == "192.168.1.100"


# --- Connection Tests ---
@pytest.mark.asyncio
async def test_connect_success(reader):
    """Test successful connection."""
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.recv.side_effect = BlockingIOError()  # No buffered data

        with patch.object(reader, "get_reader_info", new_callable=AsyncMock) as mock_info:
            mock_info.return_value = {"connected": True, "serial_number": "SN123"}
            result = await reader.connect()

            assert result is True
            assert reader.is_connected is True
            mock_sock.connect.assert_called_once()


@pytest.mark.asyncio
async def test_connect_already_connected(reader):
    """Test connect returns True when already connected."""
    reader.is_connected = True
    result = await reader.connect()
    assert result is True


@pytest.mark.asyncio
async def test_connect_timeout(reader):
    """Test connection timeout handling."""
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.connect.side_effect = socket.timeout()

        result = await reader.connect()

        assert result is False
        assert reader.is_connected is False


@pytest.mark.asyncio
async def test_connect_refused(reader):
    """Test connection refused handling."""
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock
        mock_sock.connect.side_effect = ConnectionRefusedError()

        result = await reader.connect()

        assert result is False
        assert reader.is_connected is False


# --- Disconnection Tests ---
@pytest.mark.asyncio
async def test_disconnect_when_connected(reader):
    """Test disconnect closes socket."""
    reader.is_connected = True
    reader._socket = MagicMock()

    await reader.disconnect()

    assert reader.is_connected is False
    assert reader._socket is None


@pytest.mark.asyncio
async def test_disconnect_when_not_connected(reader):
    """Test disconnect when already disconnected."""
    reader.is_connected = False
    await reader.disconnect()
    assert reader.is_connected is False


@pytest.mark.asyncio
async def test_disconnect_stops_scanning_first(reader):
    """Test disconnect stops scanning before closing."""
    reader.is_connected = True
    reader.is_scanning = True
    reader._socket = MagicMock()

    with patch.object(reader, "stop_scanning", new_callable=AsyncMock) as mock_stop:
        await reader.disconnect()
        mock_stop.assert_called_once()


# --- Command Sending Tests ---
def test_send_command_basic(reader):
    """Test _send_command sends and receives data."""
    reader.is_connected = True
    mock_sock = MagicMock()

    # Build a valid response frame
    header = struct.pack(">BBHB", HEAD, 0x00, 0x0070, 0x01)
    body = bytes([0x00])
    frame_no_crc = header + body
    crc = calculate_crc16(frame_no_crc)
    response = frame_no_crc + struct.pack(">H", crc)

    mock_sock.recv.return_value = response
    reader._socket = mock_sock

    cmd = M200Command(0x0070)
    result = reader._send_command(cmd)

    # Verify command was sent
    mock_sock.sendall.assert_called_once()
    # Verify response contains expected frame
    assert response in result



# --- Alias Method Tests ---
@pytest.mark.asyncio
async def test_get_all_config_alias(reader):
    """Test get_all_config alias calls get_all_params."""
    with patch.object(reader, "get_all_params", new_callable=AsyncMock) as mock:
        mock.return_value = {"param": "value"}
        result = await reader.get_all_config()
        mock.assert_called_once()
        assert result["param"] == "value"


@pytest.mark.asyncio
async def test_set_network_alias(reader):
    """Test set_network alias calls set_network_config."""
    with patch.object(reader, "set_network_config", new_callable=AsyncMock) as mock:
        mock.return_value = True
        result = await reader.set_network("192.168.1.50", "255.255.255.0", "192.168.1.1", 4001)
        mock.assert_called_once()
        assert result is True


def test_send_command_alias(reader):
    """Test send_command alias calls _send_command."""
    with patch.object(reader, "_send_command") as mock:
        mock.return_value = b"response"
        cmd = M200Command(0x0070)
        result = reader.send_command(cmd)
        mock.assert_called_once_with(cmd)
        assert result == b"response"
