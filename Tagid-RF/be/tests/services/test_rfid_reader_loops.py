"""
Tests for RFID Reader loops and error handling logic.
Covers read_single_tag, _scan_loop, and connection resiliency.
"""
import pytest
import asyncio
import socket
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rfid_reader import RFIDReaderService
from app.services.m200_protocol import M200Status, M200Commands, HEAD


@pytest.fixture
def reader():
    service = RFIDReaderService()
    service.is_connected = True
    service._socket = MagicMock()
    return service


# --- read_single_tag Tests ---
@pytest.mark.asyncio
async def test_read_single_tag_success(reader):
    """Test read_single_tag parsing a valid tag response."""
    mock_response = bytes([HEAD, 0x05, 0x01, M200Commands.RFM_INVENTORYISO_CONTINUE, 0x01, 0x00, 0x00, 0x00])
    
    mock_parsed = MagicMock()
    mock_parsed.status = M200Status.SUCCESS
    mock_parsed.success = True
    mock_parsed.data = [
        {"epc": "E2001", "rssi": -50, "antenna_port": 1}
    ]
    
    mock_tags = [{"epc": "E2001", "rssi": -50, "antenna_port": 1}]
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_parsed), \
         patch("app.services.rfid_reader.parse_inventory_response", return_value=mock_tags), \
         patch.object(reader, "_send_command", return_value=mock_response):
             tags = await reader.read_single_tag()
             
             assert len(tags) == 1
             assert tags[0]["epc"] == "E2001"
             assert "timestamp" in tags[0]


@pytest.mark.asyncio
async def test_read_single_tag_inventory_complete(reader):
    """Test read_single_tag handling INVENTORY_COMPLETE (no tags)."""
    mock_parsed = MagicMock()
    mock_parsed.status = M200Status.INVENTORY_COMPLETE
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_parsed):
        with patch.object(reader, "_send_command", return_value=b"raw_bytes"):
             tags = await reader.read_single_tag()
             assert tags == []


@pytest.mark.asyncio
async def test_read_single_tag_failure(reader):
    """Test read_single_tag handling device failure response."""
    mock_parsed = MagicMock()
    mock_parsed.status = M200Status.COMMAND_FAILED
    mock_parsed.success = False
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_parsed):
        with patch.object(reader, "_send_command", return_value=b"raw_bytes"):
             tags = await reader.read_single_tag()
             assert tags == []


@pytest.mark.asyncio
async def test_read_single_tag_socket_timeout(reader):
    """Test read_single_tag handling socket timeout."""
    with patch.object(reader, "_send_command", side_effect=socket.timeout):
         tags = await reader.read_single_tag()
         assert tags == []


@pytest.mark.asyncio
async def test_read_single_tag_general_exception(reader):
    """Test read_single_tag handling generic error."""
    with patch.object(reader, "_send_command", side_effect=ValueError("Encode error")):
         tags = await reader.read_single_tag()
         assert tags == []


# --- _scan_loop Tests ---
@pytest.mark.asyncio
async def test_scan_loop_runs_and_stops(reader):
    """Test _scan_loop runs and processes tags until stopped."""
    reader.is_scanning = True
    
    scan_count = 0
    
    async def mock_read():
        nonlocal scan_count
        scan_count += 1
        if scan_count > 1:
            reader.is_scanning = False # Stop loop
            return []
        return [{"epc": "TEST1", "rssi": -60}]

    callback = AsyncMock()
    reader.read_single_tag = mock_read
    
    with patch.object(reader, "_process_tag", new_callable=AsyncMock):
        await reader._scan_loop(callback)
    
    assert scan_count == 2


@pytest.mark.asyncio
async def test_scan_loop_calls_callback(reader):
    """Test _scan_loop calls the callback for found tags."""
    reader.is_scanning = True
    
    async def mock_read():
        reader.is_scanning = False # Stop after one read
        return [{"epc": "CB_TEST", "rssi": -55}]

    reader.read_single_tag = mock_read
    mock_cb = AsyncMock()
    
    with patch.object(reader, "_process_tag", new_callable=AsyncMock) as mock_process:
        await reader._scan_loop(mock_cb)
        
        mock_process.assert_called_once()
        call_args = mock_process.call_args
        assert call_args[0][0]["epc"] == "CB_TEST"
        assert call_args[0][1] == mock_cb


# --- _process_tag Tests ---
@pytest.mark.asyncio
async def test_process_tag_logic(reader):
    """Test _process_tag handles callback and deduplication."""
    tag_data = {"epc": "P1", "rssi": -50, "antenna_port": 1}
    
    called_with = []
    def mock_callback(data):
        called_with.append(data)

    # Patch everything that _process_tag uses
    with patch("app.services.rfid_reader.SessionLocal") as mock_session_local, \
         patch("app.services.rfid_reader.manager") as mock_manager, \
         patch("app.services.rfid_reader.RFIDTag") as mock_tag_cls, \
         patch("app.services.rfid_reader.RFIDScanHistory") as mock_hist_cls, \
         patch("app.db.prisma.prisma_client") as mock_prisma:
             
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Ensure all awaited objects return AsyncMocks or are AsyncMocks themselves
        mock_manager.broadcast = AsyncMock()
        mock_prisma.client.tagmapping.find_unique = AsyncMock(return_value=None)
        
        # Mock class instantiations
        mock_tag_obj = MagicMock()
        mock_tag_obj.id = 1
        mock_tag_cls.return_value = mock_tag_obj
        
        # Run the method
        await reader._process_tag(tag_data, mock_callback)
        
        # Verify callback was called
        assert len(called_with) == 1
        assert called_with[0]["epc"] == "P1"
        assert mock_manager.broadcast.called
