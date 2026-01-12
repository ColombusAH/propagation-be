import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.rfid_reader import RFIDReaderService

@pytest.mark.asyncio
async def test_read_single_tag_not_connected():
    """Test read_single_tag when not connected."""
    service = RFIDReaderService()
    service.is_connected = False
    result = await service.read_single_tag()
    assert result is None

@pytest.mark.asyncio
async def test_write_tag_not_connected():
    """Test write_tag when not connected."""
    service = RFIDReaderService()
    service.is_connected = False
    result = await service.write_tag("E2001234", {"data": "test"})
    assert result is False

@pytest.mark.asyncio
async def test_write_tag_connected():
    """Test write_tag when connected (not implemented)."""
    service = RFIDReaderService()
    service.is_connected = True
    result = await service.write_tag("E2001234", {"data": "test"})
    assert result is False  # Returns False since not implemented

@pytest.mark.asyncio
async def test_get_reader_info_not_connected():
    """Test get_reader_info when not connected."""
    service = RFIDReaderService()
    service.is_connected = False
    result = await service.get_reader_info()
    assert result["connected"] is False

@pytest.mark.asyncio
async def test_get_reader_info_connected():
    """Test get_reader_info when connected."""
    service = RFIDReaderService()
    service.is_connected = True
    result = await service.get_reader_info()
    assert result["connected"] is True
    assert "model" in result

@pytest.mark.asyncio
async def test_stop_scanning():
    """Test stop_scanning."""
    service = RFIDReaderService()
    service.is_scanning = True
    await service.stop_scanning()
    assert service.is_scanning is False

@pytest.mark.asyncio
async def test_start_scanning_not_connected():
    """Test start_scanning when not connected."""
    service = RFIDReaderService()
    service.is_connected = False
    await service.start_scanning()
    assert service.is_scanning is False

@pytest.mark.asyncio
async def test_start_scanning_already_scanning():
    """Test start_scanning when already scanning."""
    service = RFIDReaderService()
    service.is_connected = True
    service.is_scanning = True
    await service.start_scanning()
    # Should still be scanning, no error
    assert service.is_scanning is True

@pytest.mark.asyncio
async def test_connect_unknown_type():
    """Test connect with unknown connection type."""
    service = RFIDReaderService()
    service.simulation_mode = False
    service.connection_type = "unknown"
    result = await service.connect()
    assert result is False

@pytest.mark.asyncio
async def test_parse_tag():
    """Test _parse_tag method."""
    service = RFIDReaderService()
    result = service._parse_tag({"raw": "data"})
    assert "epc" in result
    assert "timestamp" in result
