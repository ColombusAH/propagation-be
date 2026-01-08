"""
Correct unit tests for app.models.store module.
"""

import pytest


@pytest.mark.unit
class TestStoreModel:
    """Tests for Store model."""

    def test_store_model_fields(self):
        """Test Store model has expected fields."""
        from app.models.store import Store
        
        # Check fields exist
        assert hasattr(Store, 'id')
        assert hasattr(Store, 'name')
        assert hasattr(Store, 'address')
        assert hasattr(Store, 'phone')
        assert hasattr(Store, 'is_active')
        assert hasattr(Store, 'created_at')
        assert hasattr(Store, 'updated_at')
        assert hasattr(Store, 'users')

    def test_store_model_instantiation(self):
        """Test Store model can be instantiated."""
        from app.models.store import Store
        
        store = Store(
            name="Test Store",
            address="123 Main St",
            phone="123-456-7890"
        )
        assert store.name == "Test Store"
        assert store.phone == "123-456-7890"


@pytest.mark.unit
class TestUserModel:
    """Tests for User model."""

    def test_user_model_fields(self):
        """Test User model has expected fields."""
        from app.models.store import User
        
        assert hasattr(User, 'id')
        assert hasattr(User, 'name')
        assert hasattr(User, 'email')
        assert hasattr(User, 'role')
        assert hasattr(User, 'store_id')
        assert hasattr(User, 'store')
        assert hasattr(User, 'notification_preferences')

    def test_user_model_instantiation(self):
        """Test User model can be instantiated."""
        from app.models.store import User
        
        user = User(
            name="Test User",
            email="test@example.com",
            role="MANAGER",
            store_id=1
        )
        assert user.name == "Test User"
        assert user.role == "MANAGER"


@pytest.mark.unit
class TestNotificationPreferenceModel:
    """Tests for NotificationPreference model."""

    def test_preference_model_fields(self):
        """Test NotificationPreference model has expected fields."""
        from app.models.store import NotificationPreference
        
        assert hasattr(NotificationPreference, 'user_id')
        assert hasattr(NotificationPreference, 'notification_type')
        assert hasattr(NotificationPreference, 'channel_push')
        assert hasattr(NotificationPreference, 'channel_sms')
        assert hasattr(NotificationPreference, 'channel_email')
        assert hasattr(NotificationPreference, 'store_filter_id')

    def test_preference_model_instantiation(self):
        """Test NotificationPreference model can be instantiated."""
        from app.models.store import NotificationPreference
        
        pref = NotificationPreference(
            user_id=1,
            notification_type="SALE",
            channel_push=True,
            channel_sms=False
        )
        assert pref.notification_type == "SALE"
        assert pref.channel_push is True


@pytest.mark.unit
class TestNotificationModel:
    """Tests for Notification model."""

    def test_notification_model_fields(self):
        """Test Notification model has expected fields."""
        from app.models.store import Notification
        
        assert hasattr(Notification, 'user_id')
        assert hasattr(Notification, 'notification_type')
        assert hasattr(Notification, 'title')
        assert hasattr(Notification, 'message')
        assert hasattr(Notification, 'sent_push')
        assert hasattr(Notification, 'is_read')
        assert hasattr(Notification, 'tag_epc')

    def test_notification_model_instantiation(self):
        """Test Notification model can be instantiated."""
        from app.models.store import Notification
        
        notif = Notification(
            user_id=1,
            notification_type="ALERT",
            title="Test Alert",
            message="This is a test",
            sent_push=True
        )
        assert notif.title == "Test Alert"
        assert notif.sent_push is True
