import socket
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.m200_protocol import HEAD, M200Command
from app.services.rfid_reader import RFIDReaderService


@pytest.fixture
def reader():
    return RFIDReaderService()


@pytest.mark.asyncio
async def test_connect_missing_info(reader):
    """Test connection success but missing reader info (line 144)."""
    with patch("socket.socket") as mock_socket_cls:
        mock_sock = mock_socket_cls.return_value
        mock_sock.recv.side_effect = BlockingIOError()

        with patch.object(
            reader, "get_reader_info", new_callable=AsyncMock
        ) as mock_info:
            mock_info.return_value = {"connected": False}
            result = await reader.connect()
            assert result is True
            assert reader.is_connected is True
            # This covers line 144 (warning)


@pytest.mark.asyncio
async def test_connect_connection_refused(reader):
    """Test connection failure due to connection refused."""
    with patch("socket.socket") as mock_socket_cls:
        mock_socket = mock_socket_cls.return_value
        mock_socket.connect.side_effect = ConnectionRefusedError()

        result = await reader.connect()
        assert result is False
        assert reader.is_connected is False


@pytest.mark.asyncio
async def test_send_command_not_connected(reader):
    """Test sending command when not connected."""
    reader.is_connected = False
    with pytest.raises(ConnectionError, match="Not connected"):
        reader._send_command(M200Command(0x01, b""))


@pytest.mark.asyncio
async def test_send_command_protocol_mismatch(reader):
    """Test handling of protocol mismatch (wrong HEAD byte)."""
    reader.is_connected = True
    reader._socket = MagicMock()
    # Return a byte that is NOT the protocol HEAD (0xCF)
    reader._socket.recv.side_effect = [b"\x00", b"some data"]

    command = M200Command(0x01, b"")
    response = reader._send_command(command)

    assert response.startswith(b"\x00")
    # Coverage for lines 223-236 in rfid_reader.py


@pytest.mark.asyncio
async def test_send_command_connection_closed(reader):
    """Test handling of connection closed during receive."""
    reader.is_connected = True
    reader._socket = MagicMock()
    reader._socket.recv.return_value = b""  # Connection closed

    command = M200Command(0x01, b"")
    with pytest.raises(ConnectionError, match="Connection closed"):
        reader._send_command(command)


@pytest.mark.asyncio
async def test_send_command_short_header(reader):
    """Test handling of responses that are too short to be a valid header."""
    reader.is_connected = True
    reader._socket = MagicMock()
    # HEAD, then EOF
    reader._socket.recv.side_effect = [bytes([HEAD]), b""]

    command = M200Command(0x01, b"")
    with pytest.raises(ConnectionError, match="Connection closed"):
        reader._send_command(command)


@pytest.mark.asyncio
async def test_send_command_read_timeout_with_partial_data(reader):
    """Test handling of read timeout after receiving partial data."""
    reader.is_connected = True
    reader._socket = MagicMock()
    # Return one byte, then timeout
    reader._socket.recv.side_effect = [bytes([HEAD]), socket.timeout()]

    command = M200Command(0x01, b"")
    response = reader._send_command(command)
    assert response == bytes([HEAD])
    # Coverage for lines 281-283
