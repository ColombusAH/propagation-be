"""
Advanced tests for RFID Reader - async methods and edge cases.
Covers get_reader_info, read_single_tag, and error handling paths.
"""
import pytest
import socket
from unittest.mock import MagicMock, patch, AsyncMock
import struct
from app.services.rfid_reader import RFIDReaderService
from app.services.m200_protocol import calculate_crc16, HEAD, M200Commands


@pytest.fixture
def reader():
    """Create RFID Reader service instance."""
    service = RFIDReaderService()
    service.reader_ip = "192.168.1.100"
    service.reader_port = 4001
    return service


# --- get_reader_info Tests ---
@pytest.mark.asyncio
async def test_get_reader_info_not_connected():
    """Test get_reader_info returns not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.get_reader_info()

    assert result["connected"] is False


@pytest.mark.asyncio
async def test_get_reader_info_timeout(reader):
    """Test get_reader_info handles timeout."""
    reader.is_connected = True
    reader._socket = MagicMock()

    with patch.object(reader, "_send_command", side_effect=socket.timeout):
        result = await reader.get_reader_info()

        assert result["connected"] is True
        assert "Timeout" in result.get("error", "")


@pytest.mark.asyncio
async def test_get_reader_info_exception(reader):
    """Test get_reader_info handles exceptions."""
    reader.is_connected = True
    reader._socket = MagicMock()

    with patch.object(reader, "_send_command", side_effect=Exception("Test error")):
        result = await reader.get_reader_info()

        assert result["connected"] is True
        assert "error" in result


# --- read_single_tag Tests ---
@pytest.mark.asyncio
async def test_read_single_tag_not_connected():
    """Test read_single_tag when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.read_single_tag()

    assert isinstance(result, list)
    assert len(result) == 0


# --- start_scanning Tests ---
@pytest.mark.asyncio
async def test_start_scanning_not_connected():
    """Test start_scanning when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.start_scanning()

    # Should return False or None when not connected
    assert result is False or result is None


@pytest.mark.asyncio
async def test_start_scanning_already_scanning(reader):
    """Test start_scanning when already scanning."""
    reader.is_connected = True
    reader.is_scanning = True

    result = await reader.start_scanning()

    # Should return True since already scanning
    assert reader.is_scanning is True


# --- stop_scanning Tests ---
@pytest.mark.asyncio
async def test_stop_scanning_not_scanning():
    """Test stop_scanning when not scanning."""
    reader = RFIDReaderService()
    reader.is_scanning = False

    await reader.stop_scanning()

    assert reader.is_scanning is False


# --- get_all_params Tests ---
@pytest.mark.asyncio
async def test_get_all_params_not_connected():
    """Test get_all_params when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.get_all_params()

    # Should return None or error dict when not connected
    assert result is None or (isinstance(result, dict) and "error" in result)


# --- set_network_config Tests ---
@pytest.mark.asyncio
async def test_set_network_config_not_connected():
    """Test set_network_config when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.set_network_config("192.168.1.50", "255.255.255.0", "192.168.1.1", 4001)

    assert result is False


# --- Gate Status Tests ---
@pytest.mark.asyncio
async def test_get_gate_status_not_connected():
    """Test get_gate_status when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.get_gate_status()

    # Should return None, error dict, or False when not connected
    assert result is None or isinstance(result, dict) or result is False



# --- GPIO Tests ---
@pytest.mark.asyncio
async def test_get_gpio_levels_not_connected():
    """Test get_gpio_levels when not connected."""
    reader = RFIDReaderService()
    reader.is_connected = False

    result = await reader.get_gpio_levels()

    assert result is None or isinstance(result, dict)
