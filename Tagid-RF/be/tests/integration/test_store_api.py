"""
Integration tests for Store API endpoints.
Note: These tests verify endpoint routing without database connections.
For full integration tests, use a separate test database.
"""

import pytest


@pytest.mark.integration
class TestStoreSchemas:
    """Test Store API schemas without database."""

    def test_store_create_schema_validation(self):
        """Test StoreCreate schema validates correctly."""
        from app.routers.stores import StoreCreate
        
        store = StoreCreate(name="Test Store", address="123 Main St")
        assert store.name == "Test Store"
        assert store.address == "123 Main St"

    def test_store_create_requires_name(self):
        """Test StoreCreate requires name field."""
        from pydantic import ValidationError
        from app.routers.stores import StoreCreate
        
        with pytest.raises(ValidationError):
            StoreCreate(address="123 Main St")  # Missing name

    def test_store_response_schema(self):
        """Test StoreResponse schema."""
        from app.routers.stores import StoreResponse
        
        response = StoreResponse(
            id=1,
            name="Test Store",
            address="123 Main St",
            phone="03-1234567",
            is_active=True,
            seller_count=5,
            manager_name="John Doe"
        )
        assert response.id == 1
        assert response.seller_count == 5


@pytest.mark.integration
class TestUserSchemas:
    """Test User API schemas without database."""

    def test_user_create_schema_validation(self):
        """Test UserCreate schema validates correctly."""
        from app.routers.users import UserCreate
        
        user = UserCreate(name="Test User", email="test@example.com")
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == "SELLER"  # Default

    def test_user_create_email_validation(self):
        """Test UserCreate validates email format."""
        from pydantic import ValidationError
        from app.routers.users import UserCreate
        
        with pytest.raises(ValidationError):
            UserCreate(name="Test", email="not-an-email")

    def test_user_response_schema(self):
        """Test UserResponse schema."""
        from app.routers.users import UserResponse
        
        response = UserResponse(
            id=1,
            name="Test User",
            email="test@example.com",
            phone="054-1234567",
            role="MANAGER",
            store_id=2,
            store_name="Test Store",
            is_active=True
        )
        assert response.role == "MANAGER"


@pytest.mark.integration
class TestNotificationSchemas:
    """Test Notification API schemas."""

    def test_notification_preference_update(self):
        """Test NotificationPreferenceUpdate schema."""
        from app.routers.notifications import NotificationPreferenceUpdate
        
        pref = NotificationPreferenceUpdate(
            notification_type="SALE",
            channel_push=True,
            channel_sms=False
        )
        assert pref.notification_type == "SALE"
        assert pref.channel_push is True

    def test_notification_types_defined(self):
        """Test NOTIFICATION_TYPES constant exists."""
        from app.routers.notifications import NOTIFICATION_TYPES
        
        assert "UNPAID_EXIT" in NOTIFICATION_TYPES
        assert "SALE" in NOTIFICATION_TYPES
        assert len(NOTIFICATION_TYPES) == 7


@pytest.mark.integration
class TestExitScanSchemas:
    """Test Exit Scan API schemas."""

    def test_exit_scan_request_schema(self):
        """Test ExitScanRequest schema."""
        from app.routers.exit_scan import ExitScanRequest
        
        request = ExitScanRequest(epcs=["E200-001", "E200-002"])
        assert len(request.epcs) == 2
        assert request.gate_id == "main-exit"  # Default

    def test_exit_scan_response_schema(self):
        """Test ExitScanResponse schema."""
        from app.routers.exit_scan import ExitScanResponse
        
        response = ExitScanResponse(
            total_scanned=5,
            paid_count=4,
            unpaid_count=1,
            unpaid_items=[],
            alert_sent=True,
            alert_recipients=3
        )
        assert response.total_scanned == 5
        assert response.alert_sent is True

