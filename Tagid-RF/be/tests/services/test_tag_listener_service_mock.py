"""
Mock-based tests for Tag Listener Service.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.services.tag_listener_service import TagListenerService
from tests.mock_utils import MockModel
from datetime import datetime

class TestTagListenerServiceMock:
    
    def setup_method(self):
        self.service = TagListenerService()

    @patch("app.services.tag_listener_service.start_inventory")
    def test_start_scan(self, mock_start):
        mock_start.return_value = True
        assert self.service.start_scan() is True
        mock_start.assert_called_once()

    @patch("app.services.tag_listener_service.stop_inventory")
    def test_stop_scan(self, mock_stop):
        mock_stop.return_value = True
        assert self.service.stop_scan() is True
        mock_stop.assert_called_once()

    @patch("app.services.tag_listener_service.threading.Thread")
    def test_start_service(self, mock_thread):
        self.service._running = False
        self.service.start()
        assert self.service._running is True
        mock_thread.return_value.start.assert_called_once()
        
    def test_stop_service(self):
        self.service._running = True
        self.service.stop()
        assert self.service._running is False

    @patch("app.services.tag_listener_service.manager")
    @patch("app.db.prisma.prisma_client")
    async def test_broadcast_tag_basic(self, mock_prisma_wrapper, mock_manager):
        """Test broadcasting a simple tag scan."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance
        
        # Reader lookup fails/returns None
        mock_db.rfidreader.find_unique = AsyncMock(return_value=None)
        # Tag lookup finds tag
        tag = MockModel(id="t1", epc="E1", productDescription="Desc", isPaid=False)
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        
        # Ensure broadcast is an AsyncMock
        mock_manager.broadcast = AsyncMock()
        
        data = {"epc": "E1", "tag_id": "tid1", "rssi": -50}
        
        await self.service._broadcast_tag(data)
        
        # Verify broadcast
        mock_manager.broadcast.assert_called_once()
        call_args = mock_manager.broadcast.call_args[0][0]
        assert call_args["type"] == "tag_scanned"
        assert call_args["data"]["epc"] == "E1"
        assert call_args["data"]["product_name"] == "Desc"

    @patch("app.services.tag_listener_service.manager")
    @patch("app.db.prisma.prisma_client")
    async def test_broadcast_tag_encrypted(self, mock_prisma_wrapper, mock_manager):
        """Test broadcasting an encrypted tag."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance
        
        mock_db.rfidreader.find_unique = AsyncMock(return_value=None)
        
        # Tag with encryption
        tag = MockModel(id="t1", epc="E1", encryptedQr="ENC_DATA")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        
        # Ensure broadcast is an AsyncMock
        mock_manager.broadcast = AsyncMock()
        
        # Mock encryption service
        with patch("app.services.tag_encryption.get_encryption_service") as mock_get_enc:
            mock_svc = MagicMock()
            mock_svc.decrypt_qr.return_value = "DECRYPTED"
            mock_get_enc.return_value = mock_svc
            
            data = {"epc": "E1"}
            await self.service._broadcast_tag(data)
            
            mock_manager.broadcast.assert_called()
            call_args = mock_manager.broadcast.call_args[0][0]
            assert call_args["data"]["is_encrypted"] is True
            assert call_args["data"]["decrypted_qr"] == "DECRYPTED"

    @patch("app.services.theft_detection.TheftDetectionService")
    @patch("app.services.tag_listener_service.manager")
    @patch("app.db.prisma.prisma_client")
    async def test_broadcast_theft_alert(self, mock_prisma_wrapper, mock_manager, mock_theft_cls):
        """Test theft alert triggering at gate."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance
        
        # Reader is GATE
        reader = MockModel(id="r1", name="Gate 1", type="GATE", location="Exit")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)
        
        tag = MockModel(id="t1", epc="E1", isPaid=False, productDescription="Stolen Item")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        
        # Mock Theft Service to report unpaid
        mock_theft_instance = mock_theft_cls.return_value
        mock_theft_instance.check_tag_payment_status = AsyncMock(return_value=False)
        
        # Ensure broadcast is an AsyncMock
        mock_manager.broadcast = AsyncMock()
        
        data = {"epc": "E1", "reader_ip": "1.1.1.1"}
        
        await self.service._broadcast_tag(data)
        
        # Should broadcast twice: scan and alert
        assert mock_manager.broadcast.call_count == 2
        
        # Check second call for alert
        alert_call = mock_manager.broadcast.call_args_list[1][0][0]
        assert alert_call["type"] == "theft_alert"
        assert "Unpaid item detected" in alert_call["data"]["message"]

    @patch("app.services.theft_detection.TheftDetectionService")
    @patch("app.services.tag_listener_service.manager")
    @patch("app.db.prisma.prisma_client")
    async def test_broadcast_gate_paid(self, mock_prisma_wrapper, mock_manager, mock_theft_cls):
        """Test paid item at gate (no alert)."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance
        
        reader = MockModel(id="r1", type="GATE")
        mock_db.rfidreader.find_unique = AsyncMock(return_value=reader)
        
        tag = MockModel(id="t1", epc="E1", isPaid=True)
        mock_db.rfidtag.find_unique = AsyncMock(return_value=tag)
        
        mock_theft_instance = mock_theft_cls.return_value
        mock_theft_instance.check_tag_payment_status = AsyncMock(return_value=True)
        
        # Ensure broadcast is an AsyncMock
        mock_manager.broadcast = AsyncMock()
        
        data = {"epc": "E1", "reader_ip": "1.1.1.1"}
        
        await self.service._broadcast_tag(data)
        
        # Scan broadcast only
        assert mock_manager.broadcast.call_count == 1
        assert mock_manager.broadcast.call_args[0][0]["type"] == "tag_scanned"

    def test_get_stats(self):
        """Test stats retrieval."""
        stats = self.service.get_stats()
        assert "total_scans" in stats
        assert "unique_epcs" in stats

    def test_on_tag_scanned_sync_with_error(self):
        """Test the sync callback with an error-prone callback."""
        def error_cb(tag):
            raise Exception("Callback Error")
            
        self.service.add_tag_callback(error_cb)
        # Should not raise exception
        self.service.on_tag_scanned_sync({"epc": "E1"})
        assert True

    @patch("app.services.tag_listener_service.manager")
    @patch("app.db.prisma.prisma_client")
    async def test_broadcast_tag_decryption_error(self, mock_prisma_wrapper, mock_manager):
        """Test QR decryption error path."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance
        
        mock_tag = MockModel(id="t1", epc="E1", encryptedQr="BAD_QR")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=mock_tag)
        mock_db.rfidreader.find_unique = AsyncMock(return_value=None)
        
        mock_manager.broadcast = AsyncMock()
        
        with patch("app.services.tag_encryption.get_encryption_service") as mock_get_enc:
            mock_enc = MagicMock()
            mock_enc.decrypt_qr.side_effect = Exception("Decrypt Error")
            mock_get_enc.return_value = mock_enc
            
            # Should not raise exception, but log it
            await self.service._broadcast_tag({"epc": "E1"})
            assert True

    def test_get_recent_tags(self):
        """Test get_recent_tags delegates to tag_store."""
        with patch("app.services.tag_listener_service.tag_store") as mock_store:
            mock_store.get_recent.return_value = [{"epc": "E1"}]
            result = self.service.get_recent_tags(10)
            assert len(result) == 1
            assert result[0]["epc"] == "E1"
            mock_store.get_recent.assert_called_with(10)

    def test_start_already_running(self):
        """Test start() when already running."""
        self.service._running = True
        with patch("app.services.tag_listener_service.threading.Thread") as mock_thread:
            self.service.start()
            mock_thread.assert_not_called()

    @patch("app.services.tag_listener_service.asyncio")
    def test_start_loop_capture_error(self, mock_asyncio):
        """Test start() handles no running loop gracefully."""
        self.service._running = False
        mock_asyncio.get_running_loop.side_effect = RuntimeError("No loop")
        
        with patch("app.services.tag_listener_service.threading.Thread") as mock_thread:
            self.service.start()
            assert self.service._running is True
            mock_thread.return_value.start.assert_called()

    @patch("app.services.tag_listener_service.start_server")
    def test_run_listener_error(self, mock_start_server):
        """Test _run_listener handles exceptions."""
        mock_start_server.side_effect = Exception("Bind error")
        # Should catch exception and log it (no crash)
        self.service._run_listener()
        assert True

    def test_module_functions_fallback(self):
        """Test the fallback module-level functions."""
        # reset module imports to trigger fallback if possible? 
        # Hard to do without reloading. 
        # Instead, we can import them directly if they are exposed
        from app.services.tag_listener_service import start_inventory, stop_inventory, set_tag_callback
        
        assert start_inventory() is False
        assert stop_inventory() is False
        # set_tag_callback passes silently
        set_tag_callback(print)

