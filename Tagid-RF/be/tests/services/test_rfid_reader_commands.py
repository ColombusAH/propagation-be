"""
Tests for RFID Reader command methods (relays, GPIO, power, etc.).
Focuses on simple request-response flows.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rfid_reader import RFIDReaderService
from app.services.m200_protocol import M200Status, M200Commands

@pytest.fixture
def reader():
    service = RFIDReaderService()
    service.is_connected = True
    service._socket = MagicMock()
    return service

@pytest.mark.asyncio
async def test_initialize_device_success(reader):
    """Test initialize_device success."""
    # Mock response
    mock_parsed = MagicMock()
    mock_parsed.success = True
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_parsed):
        with patch.object(reader, "_send_command", return_value=b"raw_bytes"):
            result = await reader.initialize_device()
            assert result is True

@pytest.mark.asyncio
async def test_initialize_device_failure(reader):
    """Test initialize_device failure."""
    mock_parsed = MagicMock()
    mock_parsed.success = False
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_parsed):
        with patch.object(reader, "_send_command", return_value=b"raw_bytes"):
            result = await reader.initialize_device()
            assert result is False

@pytest.mark.asyncio
async def test_set_power_success(reader):
    """Test set_power success."""
    mock_parsed = MagicMock()
    mock_parsed.success = True
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_parsed):
        with patch.object(reader, "_send_command", return_value=b"raw_bytes"):
            result = await reader.set_power(30)
            assert result is True

@pytest.mark.asyncio
async def test_read_tag_memory_success(reader):
    """Test read_tag_memory success."""
    mock_parsed = MagicMock()
    mock_parsed.success = True
    mock_parsed.data = b"\x11\x22"
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_parsed):
        with patch.object(reader, "_send_command", return_value=b"raw_bytes"):
            result = await reader.read_tag_memory(1, 0, 1)
            assert result == b"\x11\x22"

@pytest.mark.asyncio
async def test_stop_scanning_sends_command(reader):
    """Test stop_scanning sends command when connected."""
    reader.is_scanning = True
    
    # Create a Future to mock the task, so it can be awaited
    loop = asyncio.get_running_loop()
    mock_task = loop.create_future()
    mock_task.cancel = MagicMock()
    mock_task.set_result(None) # Make it complete immediately if awaited
    
    reader._scan_task = mock_task
    
    with patch.object(reader, "_send_command") as mock_send:
        await reader.stop_scanning()
        
        assert reader.is_scanning is False
        mock_send.assert_called_once() # Should verify it sends stop command
