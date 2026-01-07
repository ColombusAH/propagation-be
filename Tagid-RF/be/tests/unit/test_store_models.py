"""
Unit tests for Store model and API.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.unit
class TestStoreModel:
    """Tests for Store model."""

    def test_store_creation(self):
        """Test Store model can be instantiated."""
        from app.models.store import Store
        
        store = Store(
            name="Test Store",
            address="123 Test St",
            phone="03-1234567"
        )
        
        assert store.name == "Test Store"
        assert store.address == "123 Test St"
        assert store.phone == "03-1234567"

    def test_store_default_values(self):
        """Test Store model default values."""
        from app.models.store import Store
        
        store = Store(name="Test Store")
        
        assert store.is_active is None  # Will be True when saved
        assert store.address is None
        assert store.phone is None


@pytest.mark.unit
class TestStoreSchemas:
    """Tests for Store Pydantic schemas."""

    def test_store_create_schema(self):
        """Test StoreCreate schema validation."""
        from app.routers.stores import StoreCreate
        
        data = StoreCreate(
            name="New Store",
            address="456 Main St",
            phone="02-9876543"
        )
        
        assert data.name == "New Store"
        assert data.address == "456 Main St"
        assert data.phone == "02-9876543"

    def test_store_create_minimal(self):
        """Test StoreCreate with only required fields."""
        from app.routers.stores import StoreCreate
        
        data = StoreCreate(name="Minimal Store")
        
        assert data.name == "Minimal Store"
        assert data.address is None
        assert data.phone is None

    def test_store_update_schema(self):
        """Test StoreUpdate schema allows partial updates."""
        from app.routers.stores import StoreUpdate
        
        data = StoreUpdate(name="Updated Name")
        
        assert data.name == "Updated Name"
        assert data.address is None
        assert data.is_active is None

    def test_store_response_schema(self):
        """Test StoreResponse schema."""
        from app.routers.stores import StoreResponse
        
        data = StoreResponse(
            id=1,
            name="Test Store",
            address="123 Test St",
            phone="03-1234567",
            is_active=True,
            seller_count=5,
            manager_name="John Doe"
        )
        
        assert data.id == 1
        assert data.name == "Test Store"
        assert data.seller_count == 5
        assert data.manager_name == "John Doe"


@pytest.mark.unit
class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self):
        """Test User model can be instantiated."""
        from app.models.store import User
        
        user = User(
            name="Test User",
            email="test@example.com",
            phone="054-1234567",
            role="SELLER"
        )
        
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == "SELLER"

    def test_user_roles(self):
        """Test User model with different roles."""
        from app.models.store import User
        
        roles = ["ADMIN", "MANAGER", "SELLER", "CUSTOMER"]
        for role in roles:
            user = User(name="Test", email=f"{role.lower()}@test.com", role=role)
            assert user.role == role


@pytest.mark.unit
class TestUserSchemas:
    """Tests for User Pydantic schemas."""

    def test_user_create_schema(self):
        """Test UserCreate schema validation."""
        from app.routers.users import UserCreate
        
        data = UserCreate(
            name="New User",
            email="new@example.com",
            phone="054-9876543",
            role="SELLER",
            store_id=1
        )
        
        assert data.name == "New User"
        assert data.email == "new@example.com"
        assert data.role == "SELLER"
        assert data.store_id == 1

    def test_user_create_default_role(self):
        """Test UserCreate default role is SELLER."""
        from app.routers.users import UserCreate
        
        data = UserCreate(
            name="New User",
            email="new@example.com"
        )
        
        assert data.role == "SELLER"

    def test_user_response_schema(self):
        """Test UserResponse schema."""
        from app.routers.users import UserResponse
        
        data = UserResponse(
            id=1,
            name="Test User",
            email="test@example.com",
            phone="054-1234567",
            role="MANAGER",
            store_id=2,
            store_name="Test Store",
            is_active=True
        )
        
        assert data.id == 1
        assert data.role == "MANAGER"
        assert data.store_name == "Test Store"


@pytest.mark.unit
class TestNotificationPreferenceModel:
    """Tests for NotificationPreference model."""

    def test_notification_preference_creation(self):
        """Test NotificationPreference model."""
        from app.models.store import NotificationPreference
        
        pref = NotificationPreference(
            user_id=1,
            notification_type="SALE",
            channel_push=True,
            channel_sms=False,
            channel_email=True
        )
        
        assert pref.notification_type == "SALE"
        assert pref.channel_push is True
        assert pref.channel_sms is False
        assert pref.channel_email is True


@pytest.mark.unit
class TestNotificationModel:
    """Tests for Notification model."""

    def test_notification_creation(self):
        """Test Notification model."""
        from app.models.store import Notification
        
        notification = Notification(
            user_id=1,
            notification_type="UNPAID_EXIT",
            title="Security Alert",
            message="Unpaid item detected"
        )
        
        assert notification.notification_type == "UNPAID_EXIT"
        assert notification.title == "Security Alert"
        assert notification.is_read is None  # Will be False when saved


@pytest.mark.unit
class TestNotificationSchemas:
    """Tests for Notification Pydantic schemas."""

    def test_notification_preference_update(self):
        """Test NotificationPreferenceUpdate schema."""
        from app.routers.notifications import NotificationPreferenceUpdate
        
        data = NotificationPreferenceUpdate(
            notification_type="LOW_STOCK",
            channel_push=True,
            channel_sms=True,
            channel_email=False
        )
        
        assert data.notification_type == "LOW_STOCK"
        assert data.channel_push is True
        assert data.channel_sms is True
        assert data.channel_email is False

    def test_send_notification_request(self):
        """Test SendNotificationRequest schema."""
        from app.routers.notifications import SendNotificationRequest
        
        data = SendNotificationRequest(
            user_id=1,
            notification_type="SALE",
            title="New Sale",
            message="Sale completed",
            store_id=2,
            tag_epc="E200-123-456"
        )
        
        assert data.user_id == 1
        assert data.notification_type == "SALE"
        assert data.tag_epc == "E200-123-456"

    def test_notification_types_constant(self):
        """Test NOTIFICATION_TYPES constant."""
        from app.routers.notifications import NOTIFICATION_TYPES
        
        expected_types = [
            "UNPAID_EXIT", "SALE", "LOW_STOCK", "GOAL_ACHIEVED",
            "SYSTEM_UPDATE", "NEW_USER", "ERROR"
        ]
        
        assert NOTIFICATION_TYPES == expected_types
