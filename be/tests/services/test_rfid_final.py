import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.rfid_reader import RFIDReaderService
import asyncio

@pytest.mark.asyncio
async def test_connect_bluetooth():
    """Test bluetooth connection (not implemented)."""
    service = RFIDReaderService()
    service.simulation_mode = False
    service.connection_type = 'bluetooth'
    result = await service.connect()
    assert result is False

@pytest.mark.asyncio
async def test_connect_wifi_success():
    """Test successful WiFi connection."""
    service = RFIDReaderService()
    service.simulation_mode = False
    service.connection_type = 'wifi'
    
    mock_reader = AsyncMock()
    mock_writer = MagicMock()
    
    with patch("asyncio.open_connection", return_value=(mock_reader, mock_writer)):
        result = await service.connect()
        assert result is True
        assert service.is_connected is True

@pytest.mark.asyncio
async def test_disconnect_with_reader():
    """Test disconnect when reader has disconnect method."""
    service = RFIDReaderService()
    service.is_connected = True
    service.writer = None
    service.reader = MagicMock()
    service.reader.disconnect = AsyncMock()
    
    await service.disconnect()
    service.reader.disconnect.assert_called_once()
    assert service.is_connected is False

@pytest.mark.asyncio
async def test_process_tag_with_callback():
    """Test _process_tag with callback function."""
    service = RFIDReaderService()
    callback_called = []
    
    def my_callback(data):
        callback_called.append(data)
    
    tag_data = {"epc": "CALLBACK-TEST", "rssi": -45.0}
    
    with patch("app.services.rfid_reader.SessionLocal") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.query().filter().first.return_value = None
        
        with patch("app.services.rfid_reader.manager.broadcast", new_callable=AsyncMock):
            await service._process_tag(tag_data, my_callback)
    
    assert len(callback_called) == 1

@pytest.mark.asyncio
async def test_process_tag_update_existing():
    """Test _process_tag when tag already exists."""
    service = RFIDReaderService()
    tag_data = {"epc": "EXISTING-TAG", "rssi": -40.0, "antenna_port": 2, "location": "Zone-A"}
    
    with patch("app.services.rfid_reader.SessionLocal") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        mock_existing = MagicMock()
        mock_existing.id = 123
        mock_existing.read_count = 5
        mock_db.query().filter().first.return_value = mock_existing
        
        with patch("app.services.rfid_reader.manager.broadcast", new_callable=AsyncMock):
            await service._process_tag(tag_data)
        
        assert mock_existing.read_count == 6
