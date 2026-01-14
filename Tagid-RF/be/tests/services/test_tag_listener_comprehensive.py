"""
Tests for Tag Listener Service.
Covers start/stop scan, tag storage, and callback mechanics.
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.tag_listener_service import TagListenerService


@pytest.fixture
def service():
    return TagListenerService(port=4001)


def test_service_initialization(service):
    """Test service initializes with correct state."""
    assert service.port == 4001
    assert service._running is False
    assert service._thread is None
    assert service._callbacks == []


def test_start_scan(service):
    """Test start_scan calls underlying start_inventory."""
    with patch("app.services.tag_listener_service.start_inventory", return_value=True) as mock:
        result = service.start_scan()
        mock.assert_called_once()
        assert result is True


def test_stop_scan(service):
    """Test stop_scan calls underlying stop_inventory."""
    with patch("app.services.tag_listener_service.stop_inventory", return_value=True) as mock:
        result = service.stop_scan()
        mock.assert_called_once()
        assert result is True


def test_start_already_running(service):
    """Test that start does nothing if already running."""
    service._running = True
    # Should log warning and return early
    service.start()
    assert service._running is True


def test_get_recent_tags(service):
    """Test get_recent_tags returns data from tag_store."""
    with patch("app.services.tag_listener_service.tag_store") as mock_store:
        mock_store.get_recent.return_value = [{"epc": "E200001234"}]
        tags = service.get_recent_tags(count=10)
        mock_store.get_recent.assert_called_once_with(10)
        assert len(tags) == 1


def test_get_stats(service):
    """Test get_stats returns correct statistics."""
    with patch("app.services.tag_listener_service.tag_store") as mock_store:
        mock_store.get_unique_count.return_value = 5
        mock_store.get_total_count.return_value = 10
        stats = service.get_stats()
        assert stats["unique_epcs"] == 5
        assert stats["total_scans"] == 10
        assert stats["running"] is False


def test_add_tag_callback(service):
    """Test adding a callback adds to list."""

    def my_callback(tag):
        pass

    service.add_tag_callback(my_callback)
    assert my_callback in service._callbacks


def test_stop_service(service):
    """Test stop sets running to False."""
    service._running = True
    service.stop()
    assert service._running is False
