"""
Tests for Tag Listener Service logic including broadcasting and theft detection.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.tag_listener_service import TagListenerService

@pytest.fixture
def service():
    return TagListenerService()

# --- _broadcast_tag Tests ---
@pytest.mark.asyncio
async def test_broadcast_tag_basic(service):
    """Test basic broadcasting of tag data."""
    tag_data = {
        "tag_id": "123",
        "epc": "E200BASIC",
        "rssi": -60,
        "antenna_port": 1,
        "timestamp": "2026-01-01T12:00:00"
    }
    
    # Patch dependencies at their SOURCE because they are imported INSIDE the function
    with patch("app.db.prisma.prisma_client") as mock_prisma, \
         patch("app.services.database.SessionLocal") as mock_session_cls, \
         patch("app.routers.websocket.ConnectionManager.broadcast", new_callable=AsyncMock) as mock_broadcast:
         
        # Mock Prisma find_unique to return None (no encryption mapping)
        mock_db = AsyncMock()
        mock_db.tagmapping.find_unique.return_value = None
        mock_prisma.client = mock_db
        
        # Mock SQLAlchemy query to return None (no product info)
        mock_session = MagicMock()
        mock_session.query().filter().first.return_value = None
        mock_session_cls.return_value = mock_session
        
        await service._broadcast_tag(tag_data)
        
        # Verify broadcast called with tag data
        assert mock_broadcast.called
        call_args = mock_broadcast.call_args[0][0]
        assert call_args["type"] == "tag_scanned"
        assert call_args["data"]["epc"] == "E200BASIC"
        assert call_args["data"]["product_name"] is None


@pytest.mark.asyncio
async def test_broadcast_tag_theft_alert(service):
    """Test theft alert triggering for unpaid items."""
    tag_data = {"epc": "E200THEFT", "tag_id": "999"}
    
    with patch("app.db.prisma.prisma_client") as mock_prisma, \
         patch("app.services.database.SessionLocal") as mock_session_cls, \
         patch("app.routers.websocket.ConnectionManager.broadcast", new_callable=AsyncMock) as mock_broadcast:

        # Prisma mock
        mock_db = AsyncMock()
        mock_db.tagmapping.find_unique.return_value = None
        mock_prisma.client = mock_db
        
        # SQLAlchemy mock - return Unpaid Product
        mock_tag_db = MagicMock()
        mock_tag_db.product_name = "Expensive Watch"
        mock_tag_db.is_paid = False # Trigger alert
        
        mock_session = MagicMock()
        mock_session.query().filter().first.return_value = mock_tag_db
        mock_session_cls.return_value = mock_session
        
        await service._broadcast_tag(tag_data)
        
        # Should call broadcast twice: once for scan, once for alert
        assert mock_broadcast.call_count == 2
        
        # Check second call for alert
        alert_call = mock_broadcast.call_args_list[1][0][0]
        assert alert_call["type"] == "theft_alert"
        assert "Expensive Watch" in alert_call["data"]["message"]


@pytest.mark.asyncio
async def test_broadcast_tag_encrypted(service):
    """Test broadcasting of encrypted tag."""
    tag_data = {"epc": "E200ENC"}
    
    with patch("app.db.prisma.prisma_client") as mock_prisma, \
         patch("app.services.tag_encryption.get_encryption_service") as mock_get_svc, \
         patch("app.services.database.SessionLocal"), \
         patch("app.routers.websocket.ConnectionManager.broadcast", new_callable=AsyncMock) as mock_broadcast:

        # Prisma finds mapping
        mock_mapping = MagicMock()
        mock_mapping.encryptedQr = "ENCRYPTED_DATA"
        
        mock_db = AsyncMock()
        mock_db.tagmapping.find_unique.return_value = mock_mapping
        mock_prisma.client = mock_db
        
        # Encryption service decrypts
        mock_enc_svc = MagicMock()
        mock_enc_svc.decrypt_qr.return_value = "DECRYPTED_URL"
        mock_get_svc.return_value = mock_enc_svc
        
        await service._broadcast_tag(tag_data)
        
        # Verify decrypted data in payload
        call_args = mock_broadcast.call_args[0][0]
        data = call_args["data"]
        assert data["is_encrypted"] is True
        assert data["decrypted_qr"] == "DECRYPTED_URL"


# --- Threading/Start/Stop Tests ---
def test_start_creates_thread(service):
    """Test start method initializes thread."""
    with patch("threading.Thread") as mock_thread_cls, \
         patch("app.services.tag_listener_service.set_tag_callback"):
         
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread
        
        service.start()
        
        assert service._running is True
        mock_thread.start.assert_called_once()


def test_stop_sets_running_false(service):
    """Test stop method."""
    service._running = True
    service.stop()
    assert service._running is False


def test_on_tag_scanned_sync_dispatches(service):
    """Test synchronous callback dispatch."""
    # Test callbacks
    cb1 = MagicMock()
    service.add_tag_callback(cb1)
    
    # Mock loop handling
    service._loop = MagicMock()
    service._loop.is_running.return_value = True
    
    with patch("asyncio.run_coroutine_threadsafe") as mock_run_safe:
        service.on_tag_scanned_sync({"epc": "T1"})
        
        # Check async dispatch
        mock_run_safe.assert_called_once()
        
        # Check sync callback
        cb1.assert_called_once_with({"epc": "T1"})
