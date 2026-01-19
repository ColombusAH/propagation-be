"""
Mocked tests for Tag Listener Service.
Focuses on threading, callbacks, and data processing.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mark all tests as async by default
pytestmark = pytest.mark.asyncio


class TestTagListenerServiceMocked:
    """Tests for TagListenerService with mocking."""

    @pytest.fixture
    def service(self):
        """Fixture for TagListenerService."""
        # Force reload to clear mocks from sys.modules
        import sys

        if "app.services.tag_listener_service" in sys.modules:
            del sys.modules["app.services.tag_listener_service"]

        from app.services.tag_listener_service import TagListenerService

        return TagListenerService()

    async def test_start_stop(self, service):
        """Test starting and stopping the listener thread."""
        with (
            patch(
                "app.services.tag_listener_service.threading.Thread"
            ) as mock_thread_cls,
            patch("app.services.tag_listener_service.set_tag_callback"),
        ):

            mock_thread = MagicMock()
            mock_thread_cls.return_value = mock_thread

            service.start()
            assert service._running is True
            mock_thread_cls.assert_called_once()
            mock_thread.start.assert_called_once()

            service.stop()
            assert service._running is False

    def test_add_tag_callback(self, service):
        """Test adding callbacks."""
        cb = MagicMock()
        service.add_tag_callback(cb)
        assert cb in service._callbacks

    async def test_on_tag_scanned_sync(self, service):
        """Test processing of scanned tags from background thread."""
        tag_data = {"epc": "E1", "rssi": -60}
        cb = MagicMock()
        service.add_tag_callback(cb)

        with patch.object(service, "_broadcast_tag", new_callable=AsyncMock):
            service._loop = MagicMock()
            service._loop.is_running.return_value = True

            service.on_tag_scanned_sync(tag_data)
            cb.assert_called_with(tag_data)
            assert service._loop.call_soon_threadsafe.called

    async def test_broadcast_tag_logic(self, service):
        """Test the _broadcast_tag async logic."""
        tag_data = {"epc": "E1", "rssi": -60}

        # Patching at module level where it's used
        # SessionLocal is imported INSIDE _broadcast_tag from app.services.database
        # prisma_client is imported INSIDE _broadcast_tag from app.db.prisma
        # manager is imported at module LEVEL in tag_listener_service.py
        # get_encryption_service is imported INSIDE _broadcast_tag from app.services.tag_encryption

        with (
            patch(
                "app.services.tag_listener_service.manager", new_callable=AsyncMock
            ) as mock_manager,
            patch("app.services.database.SessionLocal") as mock_session_cls,
            patch("app.db.prisma.prisma_client") as mock_prisma,
            patch(
                "app.services.tag_encryption.get_encryption_service"
            ) as mock_get_encrypt,
        ):

            # Setup DB mock
            mock_db = MagicMock()
            mock_session_cls.return_value = mock_db
            mock_tag = MagicMock()
            mock_tag.product_name = "Test Product"
            mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

            # Setup Prisma mock properly as a context manager
            mock_prisma_client = AsyncMock()
            mock_prisma.client = mock_prisma_client
            mock_prisma_client.__aenter__.return_value = AsyncMock()

            # Setup Encryption service mock
            mock_encrypt_svc = MagicMock()
            mock_get_encrypt.return_value = mock_encrypt_svc
            mock_encrypt_svc.decrypt_qr.return_value = "DECRYPTED"

            # Setup manager mock behavior
            mock_manager.broadcast = AsyncMock()

            await service._broadcast_tag(tag_data)

            # Verify called
            assert mock_manager.broadcast.called or mock_manager.called
            assert mock_session_cls.called

    def test_get_stats(self, service):
        """Test get_stats."""
        with patch("app.services.tag_listener_service.tag_store") as mock_store:
            mock_store.get_total_count.return_value = 10
            mock_store.get_unique_count.return_value = 5

            stats = service.get_stats()
            assert stats["total_scans"] == 10
            assert stats["unique_epcs"] == 5
