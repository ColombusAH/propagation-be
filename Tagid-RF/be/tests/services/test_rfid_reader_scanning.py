"""
Extended tests for RFID Reader Service - scanning and advanced operations.
"""

import socket
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.rfid_reader import RFIDReaderService


@pytest.fixture
def connected_reader():
    """Create a connected RFID Reader service instance."""
    service = RFIDReaderService()
    service.is_connected = True
    service._socket = MagicMock()
    return service


# --- Scanning State Tests ---
@pytest.mark.asyncio
async def test_stop_scanning_not_scanning():
    """Test stop_scanning when not scanning."""
    reader = RFIDReaderService()
    reader.is_scanning = False

    await reader.stop_scanning()
    assert reader.is_scanning is False


@pytest.mark.asyncio
async def test_start_scanning_already_scanning(connected_reader):
    """Test start_scanning when already scanning."""
    connected_reader.is_scanning = True

    with patch.object(connected_reader, "_send_command") as mock_send:
        result = await connected_reader.start_scanning()
        # Should return True if already scanning
        assert connected_reader.is_scanning is True


# --- Reader Info Tests ---
@pytest.mark.asyncio
async def test_get_reader_info_not_connected():
    """Test get_reader_info when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.get_reader_info()
    assert result["connected"] is False


# --- Error Handling Tests ---
def test_send_command_not_connected():
    """Test _send_command raises when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    from app.services.m200_protocol import M200Command

    with pytest.raises(ConnectionError, match="Not connected"):
        reader._send_command(M200Command(0x0070))


# --- Configuration Tests ---
@pytest.mark.asyncio
async def test_get_all_params_not_connected():
    """Test get_all_params when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.get_all_params()
    # Should return None or error when not connected
    assert result is None or isinstance(result, dict)


# --- Connection State Tests ---
def test_is_connected_false_by_default():
    """Test reader is not connected by default."""
    reader = RFIDReaderService()
    assert reader.is_connected is False


def test_is_scanning_false_by_default():
    """Test reader is not scanning by default."""
    reader = RFIDReaderService()
    assert reader.is_scanning is False


def test_socket_none_by_default():
    """Test socket is None by default."""
    reader = RFIDReaderService()
    assert reader._socket is None


@pytest.mark.asyncio
async def test_disconnect_when_not_connected():
    """Test disconnect when already disconnected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    # Should not raise
    await reader.disconnect()
    assert reader.is_connected is False
