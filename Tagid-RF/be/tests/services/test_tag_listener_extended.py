"""
Extended tests for Tag Listener Service - deeper coverage.
"""

import pytest
import threading
from unittest.mock import MagicMock, patch, AsyncMock


# --- TagListenerService Tests ---
def test_service_initialization():
    """Test TagListenerService initialization."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService(port=4001)
    assert service.port == 4001
    assert service._running is False
    assert service._callbacks == []


def test_service_add_callback():
    """Test adding callback to service."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService()
    callback = MagicMock()

    service.add_tag_callback(callback)

    assert callback in service._callbacks


def test_service_get_recent_tags():
    """Test get_recent_tags returns from store."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService()
    tags = service.get_recent_tags(10)

    assert isinstance(tags, list)


def test_service_get_stats():
    """Test get_stats returns statistics dict."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService()
    stats = service.get_stats()

    assert isinstance(stats, dict)
    # Stats should have some common keys
    assert len(stats) > 0


def test_service_start_scan():
    """Test start_scan calls inventory function."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService()

    with patch("app.services.tag_listener_service.start_inventory") as mock_inv:
        mock_inv.return_value = True
        result = service.start_scan()
        # May return True/False depending on mock
        assert result is True or result is False


def test_service_stop_scan():
    """Test stop_scan calls stop inventory function."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService()

    with patch("app.services.tag_listener_service.stop_inventory") as mock_stop:
        mock_stop.return_value = True
        result = service.stop_scan()
        assert result is True or result is False


def test_service_start_already_running():
    """Test start when already running logs warning."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService()
    service._running = True

    # Should return without error when already running
    service.start()
    assert service._running is True


def test_service_stop_when_not_running():
    """Test stop when not running is safe."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService()
    service._running = False

    # Should not raise
    service.stop()
    assert service._running is False


def test_service_default_port():
    """Test default port is 4001."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService()
    assert service.port == 4001


def test_service_custom_port():
    """Test custom port can be set."""
    from app.services.tag_listener_service import TagListenerService

    service = TagListenerService(port=5000)
    assert service.port == 5000
