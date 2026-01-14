import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rfid_reader import RFIDReaderService
import asyncio

@pytest.fixture
def rfid_service():
    return RFIDReaderService()

@pytest.mark.asyncio
async def test_connect_failures(rfid_service):
    rfid_service.simulation_mode = False
    
    # Test Unknown connection type
    rfid_service.connection_type = "unknown_weird_type"
    assert await rfid_service.connect() is False
    
    # Test WiFi failure
    rfid_service.connection_type = "wifi"
    with patch("asyncio.open_connection", side_effect=Exception("Connection refused")):
        assert await rfid_service.connect() is False
        assert rfid_service.is_connected is False

@pytest.mark.asyncio
async def test_connect_serial_failure(rfid_service):
    rfid_service.simulation_mode = False
    rfid_service.connection_type = "serial"
    
    # Logic: ImportError
    with patch.dict('sys.modules', {'serial': None}):
        assert await rfid_service.connect() is False

    # Logic: Generic Exception
    with patch("serial.Serial", side_effect=Exception("Serial error")):
        assert await rfid_service.connect() is False

@pytest.mark.asyncio
async def test_disconnect(rfid_service):
    # Setup mock connected state
    rfid_service.is_connected = True
    rfid_service.writer = AsyncMock()
    rfid_service.reader = MagicMock()
    rfid_service.reader.disconnect = AsyncMock()
    
    await rfid_service.disconnect()
    
    assert rfid_service.is_connected is False
    rfid_service.writer.close.assert_called()
    rfid_service.writer.wait_closed.assert_called()
    rfid_service.reader.disconnect.assert_called()

@pytest.mark.asyncio
async def test_disconnect_error(rfid_service):
    rfid_service.writer = AsyncMock()
    rfid_service.writer.close.side_effect = Exception("Close error")
    
    # Should not raise exception
    await rfid_service.disconnect()

@pytest.mark.asyncio
async def test_start_scanning_checks(rfid_service):
    # Not connected
    rfid_service.is_connected = False
    await rfid_service.start_scanning()
    assert rfid_service.is_scanning is False
    
    # Already scanning
    rfid_service.is_connected = True
    rfid_service.is_scanning = True
    await rfid_service.start_scanning() 
    assert rfid_service.is_scanning is True

@pytest.mark.asyncio
async def test_read_single_tag_checks(rfid_service):
    rfid_service.is_connected = False
    assert await rfid_service.read_single_tag() is None
    
    rfid_service.is_connected = True
    assert await rfid_service.read_single_tag() is None

@pytest.mark.asyncio
async def test_write_tag_checks(rfid_service):
    rfid_service.is_connected = False
    assert await rfid_service.write_tag("E2...", {}) is False
    
    rfid_service.is_connected = True
    assert await rfid_service.write_tag("E2...", {}) is False

@pytest.mark.asyncio
async def test_process_tag_db_error(rfid_service):
    # Test DB rollback on error
    with patch("app.services.rfid_reader.SessionLocal") as mock_session_local:
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.side_effect = Exception("DB Error")
        
        await rfid_service._process_tag({"epc": "E2..."})
        
        mock_db.rollback.assert_called()
