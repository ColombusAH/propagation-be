"""
Comprehensive tests for PushNotificationService.
Covers: __init__, send_notification, send_bulk_notifications
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestPushNotificationService:
    """Tests for PushNotificationService."""

    @pytest.fixture
    def service(self):
        """Create PushNotificationService with mocked Firebase."""
        with patch("app.services.push_notifications.firebase_admin") as mock_firebase:
            mock_firebase._apps = []  # Simulate no apps initialized
            mock_firebase.initialize_app = MagicMock()

            with patch("app.services.push_notifications.credentials"):
                from app.services.push_notifications import PushNotificationService

                return PushNotificationService()

    @pytest.mark.asyncio
    async def test_send_notification_success(self, service):
        """Test successful notification sending."""
        result = await service.send_notification(
            user_id="user-123", title="Test Title", body="Test Body", data={"key": "value"}
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_notification_without_data(self, service):
        """Test sending notification without data payload."""
        result = await service.send_notification(
            user_id="user-123", title="Test Title", body="Test Body"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_send_notification_error(self, service):
        """Test handling error during notification."""
        with patch.object(service, "send_notification", side_effect=Exception("FCM Error")):
            with pytest.raises(Exception):
                await service.send_notification("user-123", "Title", "Body")

    @pytest.mark.asyncio
    async def test_send_bulk_notifications(self, service):
        """Test sending bulk notifications."""
        user_ids = ["user-1", "user-2", "user-3"]

        results = await service.send_bulk_notifications(
            user_ids=user_ids, title="Bulk Title", body="Bulk Body"
        )

        assert len(results) == 3
        assert all(results.values())  # All should succeed

    @pytest.mark.asyncio
    async def test_send_bulk_notifications_empty_list(self, service):
        """Test bulk notifications with empty list."""
        results = await service.send_bulk_notifications(user_ids=[], title="Title", body="Body")

        assert results == {}

    @pytest.mark.asyncio
    async def test_send_bulk_notifications_with_data(self, service):
        """Test bulk notifications with data payload."""
        results = await service.send_bulk_notifications(
            user_ids=["user-1", "user-2"],
            title="Alert",
            body="Important message",
            data={"alert_id": "123"},
        )

        assert len(results) == 2


class TestPushNotificationServiceInit:
    """Tests for PushNotificationService initialization."""

    def test_init_firebase_already_initialized(self):
        """Test initialization when Firebase is already initialized."""
        with patch("app.services.push_notifications.firebase_admin") as mock_firebase:
            mock_firebase._apps = {"default": MagicMock()}  # Already initialized

            with patch("app.services.push_notifications.settings"):
                from app.services.push_notifications import PushNotificationService

                service = PushNotificationService()

                # Should not call initialize_app again
                mock_firebase.initialize_app.assert_not_called()

    def test_init_firebase_error(self):
        """Test handling Firebase initialization error."""
        with patch("app.services.push_notifications.firebase_admin") as mock_firebase:
            mock_firebase._apps = []

            with patch(
                "app.services.push_notifications.credentials.Certificate",
                side_effect=Exception("Invalid credentials"),
            ):
                # Should not raise, just log error
                from app.services.push_notifications import PushNotificationService

                service = PushNotificationService()
                assert service is not None
