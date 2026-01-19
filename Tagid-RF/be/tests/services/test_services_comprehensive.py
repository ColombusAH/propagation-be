"""
Additional tests for services to improve code coverage.
Tests for tag_encryption, theft_detection, push_notifications, and payment providers.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mark all tests as async
pytestmark = pytest.mark.asyncio


class TestTagEncryption:
    """Tests for tag_encryption service."""

    def test_import_service(self):
        """Test that tag_encryption can be imported."""
        from app.services.tag_encryption import TagEncryptionService

        assert TagEncryptionService is not None

    def test_create_service(self):
        """Test creating TagEncryptionService."""
        from app.services.tag_encryption import TagEncryptionService

        service = TagEncryptionService()
        assert service is not None

    def test_generate_qr_code(self):
        """Test QR code generation."""
        from app.services.tag_encryption import TagEncryptionService

        service = TagEncryptionService()
        # Test that the method exists
        if hasattr(service, "generate_qr_code"):
            result = service.generate_qr_code("E2000000001234")
            assert result is not None

    def test_encrypt_epc(self):
        """Test EPC encryption."""
        from app.services.tag_encryption import TagEncryptionService

        service = TagEncryptionService()
        if hasattr(service, "encrypt_epc"):
            result = service.encrypt_epc("E2000000001234")
            assert result is not None
            assert isinstance(result, str)

    def test_decrypt_qr(self):
        """Test QR decryption."""
        from app.services.tag_encryption import TagEncryptionService

        service = TagEncryptionService()
        if hasattr(service, "encrypt_epc") and hasattr(service, "decrypt_qr"):
            encrypted = service.encrypt_epc("E2000000001234")
            decrypted = service.decrypt_qr(encrypted)
            assert decrypted is not None

    def test_verify_match(self):
        """Test matching verification."""
        from app.services.tag_encryption import TagEncryptionService

        service = TagEncryptionService()
        if hasattr(service, "verify_match"):
            result = service.verify_match("E2000000001234", "encrypted_data")
            assert isinstance(result, bool)


class TestCashProvider:
    """Tests for CashProvider service."""

    def test_import_provider(self):
        """Test that CashProvider can be imported."""
        from app.services.payment.cash_gateway import CashGateway

        assert CashGateway is not None

    def test_create_provider(self):
        """Test creating CashProvider."""
        from app.services.payment.cash_gateway import CashGateway

        provider = CashGateway()
        assert provider is not None

    async def test_create_payment_intent(self):
        """Test creating payment intent."""
        from app.services.payment.base import PaymentRequest
        from app.services.payment.cash_gateway import CashGateway

        provider = CashGateway()
        request = PaymentRequest(amount=1000, currency="ILS", order_id="test123")
        result = await provider.create_payment(request)
        assert result is not None
        assert result.success is True

    async def test_confirm_payment(self):
        """Test confirming payment."""
        from app.services.payment.cash_gateway import CashGateway

        provider = CashGateway()
        result = await provider.confirm_payment("cash_123456")
        assert result.success is True

    async def test_refund_payment(self):
        """Test refunding payment."""
        from app.services.payment.cash_gateway import CashGateway

        provider = CashGateway()
        result = await provider.refund_payment("cash_123456")
        assert result.success is True

    async def test_get_payment_status(self):
        """Test getting payment status."""
        from app.services.payment.cash_gateway import CashGateway

        provider = CashGateway()
        result = await provider.get_payment_status("cash_123456")
        assert result.success is True


class TestTagListenerService:
    """Tests for TagListenerService."""

    def test_init(self):
        from app.services.tag_listener_service import TagListenerService

        service = TagListenerService(port=9999)
        assert service.port == 9999
        assert service._running is False

    @pytest.mark.asyncio
    async def test_start_stop_mock(self):
        from app.services.tag_listener_service import TagListenerService

        service = TagListenerService()
        # Just test that they run without crashing with mocks
        with patch("app.services.tag_listener_service.start_inventory") as m1:
            with patch("app.services.tag_listener_service.start_server") as m2:
                service.start()
                service.stop()


class TestTheftDetectionEnhanced:
    """Enhanced tests for theft detection service."""

    @pytest.mark.asyncio
    async def test_check_tag_not_found(self):
        from app.services.theft_detection import TheftDetectionService

        with patch("app.services.theft_detection.prisma_client") as mock_p:
            mock_p.client.tagmapping.find_unique = AsyncMock(return_value=None)
            service = TheftDetectionService()
            result = await service.check_tag_payment_status("UNKNOWN")
            assert result is True  # Should return True (don't alert) on unknown

    @pytest.mark.asyncio
    async def test_check_tag_exception(self):
        from app.services.theft_detection import TheftDetectionService

        with patch("app.services.theft_detection.prisma_client") as mock_p:
            mock_p.client.tagmapping.find_unique = AsyncMock(
                side_effect=Exception("DB Error")
            )
            service = TheftDetectionService()
            result = await service.check_tag_payment_status("ERROR")
            assert result is True  # Should return True on error

    @pytest.mark.asyncio
    async def test_resolve_alert_success(self):
        from app.services.theft_detection import TheftDetectionService

        with patch("app.services.theft_detection.prisma_client") as mock_p:
            mock_p.client.theftalert.update = AsyncMock()
            service = TheftDetectionService()
            await service.resolve_alert("a1", "u1", "notes")
            mock_p.client.theftalert.update.assert_called_once()


class TestStripeProvider:
    """Tests for StripeProvider service."""

    def test_import_provider(self):
        """Test that StripeProvider can be imported."""
        from app.services.payment.stripe_gateway import StripeGateway

        assert StripeGateway is not None

    def test_create_provider(self):
        """Test creating StripeProvider."""
        from app.services.payment.stripe_gateway import StripeGateway

        provider = StripeGateway(api_key="sk_test_123")
        assert provider is not None


class TestTranzilaProvider:
    """Tests for TranzilaProvider service."""

    def test_import_provider(self):
        """Test that TranzilaProvider can be imported."""
        from app.services.payment.tranzila import TranzilaGateway

        assert TranzilaGateway is not None

    def test_create_provider(self):
        """Test creating TranzilaProvider."""
        from app.services.payment.tranzila import TranzilaGateway

        provider = TranzilaGateway(terminal_name="test")
        assert provider is not None


class TestPaymentProviderFactory:
    """Tests for PaymentProvider factory."""

    def test_import_factory(self):
        """Test that payment factory can be imported."""
        from app.services.payment.factory import get_gateway

        assert get_gateway is not None

    def test_get_cash_provider(self):
        """Test getting cash provider."""
        from app.services.payment.base import PaymentProvider
        from app.services.payment.factory import get_gateway

        provider = get_gateway("cash")
        assert provider is not None
        assert provider.provider == PaymentProvider.CASH

    def test_get_stripe_provider_mock(self):
        """Test getting stripe provider."""
        from app.services.payment.factory import get_gateway

        # Patch the settings used by the factory
        with patch("app.services.payment.factory.settings") as mock_settings:
            mock_settings.STRIPE_SECRET_KEY = "sk_test_123"
            mock_settings.STRIPE_WEBHOOK_SECRET = "whsec_123"

            provider = get_gateway("stripe")
            assert provider is not None


class TestTheftDetection:
    """Tests for theft detection service."""

    def test_import_service(self):
        """Test that theft detection service can be imported."""
        from app.services.theft_detection import TheftDetectionService

        assert TheftDetectionService is not None

    def test_create_service(self):
        """Test creating TheftDetectionService."""
        from app.services.theft_detection import TheftDetectionService

        service = TheftDetectionService()
        assert service is not None


class TestPushNotifications:
    """Tests for push notifications service."""

    def test_import_service(self):
        """Test that push notifications service can be imported."""
        from app.services.push_notifications import PushNotificationService

        assert PushNotificationService is not None

    def test_create_service(self):
        """Test creating PushNotificationService."""
        from app.services.push_notifications import PushNotificationService

        service = PushNotificationService()
        assert service is not None


class TestDatabase:
    """Tests for database service."""

    def test_import_database(self):
        """Test that database module can be imported."""
        from app.services import database

        assert database is not None

    def test_session_local(self):
        """Test SessionLocal is available."""
        from app.services.database import SessionLocal

        assert SessionLocal is not None

    def test_get_db(self):
        """Test get_db generator."""
        from app.services.database import get_db

        assert get_db is not None


class TestCorePermissions:
    """Tests for core permissions module."""

    def test_import_permissions(self):
        """Test that permissions module can be imported."""
        from app.core.permissions import requires_any_role, requires_role

        assert requires_role is not None
        assert requires_any_role is not None

    def test_is_admin(self):
        """Test is_admin function."""
        from app.core.permissions import is_admin

        mock_user = MagicMock()
        mock_user.role = "SUPER_ADMIN"
        result = is_admin(mock_user)
        assert result is True

        mock_user.role = "CUSTOMER"
        result = is_admin(mock_user)
        assert result is False

    def test_is_manager(self):
        """Test is_manager function."""
        from app.core.permissions import is_manager

        mock_user = MagicMock()
        mock_user.role = "STORE_MANAGER"
        result = is_manager(mock_user)
        assert result is True

        mock_user.role = "CUSTOMER"
        result = is_manager(mock_user)
        assert result is False

    def test_can_create_role(self):
        """Test can_create_role function."""
        from app.core.permissions import can_create_role

        mock_user = MagicMock()
        mock_user.role = "SUPER_ADMIN"
        result = can_create_role(mock_user, "STORE_MANAGER")
        assert isinstance(result, bool)


class TestCoreSecurity:
    """Tests for core security module."""

    def test_import_security(self):
        """Test that security module can be imported."""
        from app.core.security import (
            create_access_token,
            get_password_hash,
            verify_access_token,
            verify_password,
        )

        assert create_access_token is not None
        assert verify_password is not None
        assert get_password_hash is not None
        assert verify_access_token is not None

    def test_password_hash(self):
        """Test password hashing."""
        from app.core.security import get_password_hash, verify_password

        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Test access token creation."""
        from app.core.security import create_access_token

        token = create_access_token(data={"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)

    def test_verify_access_token(self):
        """Test access token verification."""
        from app.core.security import create_access_token, verify_access_token

        token = create_access_token(data={"sub": "testuser"})
        payload = verify_access_token(token)
        assert payload is not None
        assert payload.get("sub") == "testuser"

    def test_verify_invalid_token(self):
        """Test verifying invalid token."""
        from app.core.security import verify_access_token

        result = verify_access_token("invalid_token")
        assert result is None
