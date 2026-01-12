import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.rfid_reader import RFIDReaderService

@pytest.mark.asyncio
async def test_connect_wifi_error():
    """Test WiFi connection error handling."""
    service = RFIDReaderService()
    service.simulation_mode = False
    service.connection_type = 'wifi'
    
    with patch("asyncio.open_connection", side_effect=Exception("Connection refused")):
        result = await service.connect()
        assert result is False
        assert service.is_connected is False

@pytest.mark.asyncio
async def test_connect_serial_import_error():
    """Test serial connection when pyserial not installed."""
    service = RFIDReaderService()
    service.simulation_mode = False
    service.connection_type = 'serial'
    
    with patch.dict('sys.modules', {'serial': None}):
        with patch("builtins.__import__", side_effect=ImportError("No module named 'serial'")):
            result = await service.connect()
            assert result is False

@pytest.mark.asyncio
async def test_send_command_not_connected():
    """Test send_command when not connected."""
    service = RFIDReaderService()
    service.is_connected = False
    service.writer = None
    
    with pytest.raises(ConnectionError):
        await service.send_command(b"test")
