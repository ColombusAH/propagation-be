"""
Tests for RFID Reader complex logic extensions:
1. get_device_info edge cases (Protocol mismatch, JSON/HTTP handling)
2. _process_tag (Database interactions, Mapping, Encryption, WebSocket broadcast)
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.rfid_reader import RFIDReaderService
from app.services.m200_protocol import M200Commands, M200Status

@pytest.fixture
def reader():
    service = RFIDReaderService()
    service.is_connected = True
    service.reader_port = 4001
    service._socket = MagicMock()
    service.reader_id = "TEST-READER"
    return service

# --- get_device_info Edge Cases ---

@pytest.mark.asyncio
async def test_get_device_info_cmd_mismatch(reader):
    """Test handling of responses with mismatched CMD (unsolicited messages)."""
    # Mock response with WRONG CMD
    mock_parsed = MagicMock()
    mock_parsed.cmd = 0xFFFF # Some random command
    mock_parsed.success = True
    
    with patch("app.services.rfid_reader.M200ResponseParser.parse", return_value=mock_parsed) as mock_parser:
        with patch.object(reader, "_send_command", return_value=b"raw_bytes"):
            # Should interpret success despite mismatch warning
            result = await reader.get_reader_info()
            assert result.get("connected") is True
            
@pytest.mark.asyncio
async def test_get_device_info_json_http_protocol(reader):
    """Test detection of JSON/HTTP protocol (Debug port)."""
    # Simulate ValueError from binary parser
    with patch("app.services.rfid_reader.M200ResponseParser.parse", side_effect=ValueError("Invalid header")):
        
        # Mock raw bytes to look like HTTP/JSON
        raw_response = b"HTTP/1.1 200 OK\r\nContent-Length: 20\r\n\r\n{\"type\":\"event\"}"
        
        with patch.object(reader, "_send_command", return_value=raw_response):
            result = await reader.get_reader_info()
            
            assert result["connected"] is True
            assert "error" in result
            assert "Wrong protocol" in result["error"]
            assert result["protocol_detected"] == "JSON/HTTP"

# --- _process_tag Logic ---

@pytest.mark.asyncio
async def test_process_tag_new_tag_flow(reader):
    """Test processing a new tag: DB create, mapping check, broadcast."""
    tag_data = {
        "epc": "NEW_TAG_EPC",
        "rssi": -60,
        "antenna_port": 1,
        "timestamp": "2026-01-01T12:00:00"
    }

    # Patch ALL dependencies
    # Patch RFIDTag CLASS so that when it is instantiated, it returns our mock
    with patch("app.services.rfid_reader.SessionLocal") as mock_session_cls, \
         patch("app.db.prisma.prisma_client") as mock_prisma, \
         patch("app.routers.websocket.manager.broadcast", new_callable=AsyncMock) as mock_broadcast, \
         patch("app.services.rfid_reader.RFIDTag") as MockRFIDTag:
        
        # 1. DB Mock - Query returns None (New Tag)
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None 
        mock_session_cls.return_value = mock_db
        
        # Mock the RFIDTag instance
        mock_tag_instance = MagicMock()
        mock_tag_instance.id = 100
        MockRFIDTag.return_value = mock_tag_instance
        
        # 2. Prisma Mock - No mapping
        mock_prisma_client = AsyncMock()
        mock_prisma_client.tagmapping.find_unique.return_value = None
        mock_prisma.client = mock_prisma_client

        # Run method
        await reader._process_tag(tag_data)
        
        # Verifications
        # DB: Should add new tag and history
        assert mock_db.add.call_count == 2 # NewTag + History
        assert mock_db.commit.call_count == 2
        
        # WebSocket: Should broadcast
        mock_broadcast.assert_called_once()
        call_args = mock_broadcast.call_args[0][0]
        assert call_args["type"] == "tag_scanned"
        assert call_args["data"]["tag_id"] == 100
        assert call_args["data"]["epc"] == "NEW_TAG_EPC"

@pytest.mark.asyncio
async def test_process_tag_existing_tag_update(reader):
    """Test processing existing tag: DB update, broadcast."""
    tag_data = {"epc": "EXISTING_EPC", "rssi": -55, "antenna_port": 1}
    
    with patch("app.services.rfid_reader.SessionLocal") as mock_session_cls, \
         patch("app.db.prisma.prisma_client"), \
         patch("app.routers.websocket.manager.broadcast", new_callable=AsyncMock):
         
        mock_db = MagicMock()
        mock_existing_tag = MagicMock()
        mock_existing_tag.read_count = 10
        mock_existing_tag.id = 50
        
        # Query returns existing tag
        mock_db.query().filter().first.return_value = mock_existing_tag
        mock_session_cls.return_value = mock_db
        
        await reader._process_tag(tag_data)
        
        # DB: Update existing
        assert mock_existing_tag.read_count == 11
        # DB: Add history only
        assert mock_db.add.call_count == 1
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_process_tag_with_mapping(reader):
    """Test processing tag with encryption mapping."""
    tag_data = {"epc": "MAPPED_EPC"}
    
    with patch("app.services.rfid_reader.SessionLocal") as mock_session_cls, \
         patch("app.db.prisma.prisma_client") as mock_prisma, \
         patch("app.routers.websocket.manager.broadcast", new_callable=AsyncMock) as mock_broadcast:
         
        # DB Mock (Simplified)
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = MagicMock()
        mock_session_cls.return_value = mock_db
        
        # Prisma Mock - Return mapping
        mock_mapping = MagicMock()
        mock_mapping.encryptedQr = "ENCRYPTED_PAYLOAD"
        mock_client = AsyncMock()
        mock_client.tagmapping.find_unique.return_value = mock_mapping
        mock_prisma.client = mock_client
        
        await reader._process_tag(tag_data)
        
        # Verify Broadcast contains mapping info
        call_args = mock_broadcast.call_args[0][0]
        data = call_args["data"]
        assert data["is_mapped"] is True
        assert data["target_qr"] == "ENCRYPTED_PAYLOAD"
