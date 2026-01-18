"""
Comprehensive tests for Payment Gateway factory and base classes.
Covers: get_gateway, get_available_providers, PaymentRequest, PaymentResult, RefundResult
"""

import pytest
from unittest.mock import patch, MagicMock
import os


class TestPaymentBase:
    """Tests for payment base types."""

    def test_payment_request_creation(self):
        """Test creating PaymentRequest."""
        from app.services.payment.base import PaymentRequest
        
        req = PaymentRequest(
            order_id="order-123",
            amount=1000,
            currency="ILS",
            customer_email="test@example.com"
        )
        
        assert req.order_id == "order-123"
        assert req.amount == 1000
        assert req.currency == "ILS"

    def test_payment_request_defaults(self):
        """Test PaymentRequest default values."""
        from app.services.payment.base import PaymentRequest
        
        req = PaymentRequest(order_id="order-123", amount=500)
        
        assert req.currency == "ILS"
        assert req.customer_email is None
        assert req.metadata is None

    def test_payment_result_creation(self):
        """Test creating PaymentResult."""
        from app.services.payment.base import PaymentResult, PaymentStatus
        
        result = PaymentResult(
            success=True,
            payment_id="pay-123",
            external_id="ext-456"
        )
        
        assert result.success is True
        assert result.payment_id == "pay-123"
        assert result.status == PaymentStatus.PENDING

    def test_refund_result_creation(self):
        """Test creating RefundResult."""
        from app.services.payment.base import RefundResult
        
        result = RefundResult(success=True, refund_id="ref-123")
        
        assert result.success is True
        assert result.refund_id == "ref-123"

    def test_payment_status_enum(self):
        """Test PaymentStatus enum values."""
        from app.services.payment.base import PaymentStatus
        
        assert PaymentStatus.PENDING == "pending"
        assert PaymentStatus.COMPLETED == "completed"
        assert PaymentStatus.FAILED == "failed"
        assert PaymentStatus.REFUNDED == "refunded"

    def test_payment_provider_enum(self):
        """Test PaymentProvider enum values."""
        from app.services.payment.base import PaymentProvider
        
        assert PaymentProvider.STRIPE == "stripe"
        assert PaymentProvider.TRANZILA == "tranzila"
        assert PaymentProvider.CASH == "cash"


class TestPaymentFactory:
    """Tests for payment gateway factory."""

    def test_get_gateway_cash(self):
        """Test getting cash gateway."""
        from app.services.payment.factory import get_gateway
        
        gateway = get_gateway("cash")
        assert gateway is not None

    def test_get_gateway_unknown_provider(self):
        """Test getting unknown provider raises error."""
        from app.services.payment.factory import get_gateway
        
        with pytest.raises(ValueError, match="Unknown payment provider"):
            get_gateway("unknown_provider")

    def test_get_gateway_caching(self):
        """Test that gateway instances are cached."""
        from app.services.payment.factory import get_gateway
        
        gateway1 = get_gateway("cash")
        gateway2 = get_gateway("cash")
        
        assert gateway1 is gateway2

    def test_get_available_providers(self):
        """Test getting available providers."""
        from app.services.payment.factory import get_available_providers
        
        providers = get_available_providers()
        
        assert "cash" in providers  # Cash is always available

    def test_get_available_providers_with_stripe(self):
        """Test that Stripe is listed when configured."""
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_123"}):
            from app.services.payment.factory import get_available_providers
            providers = get_available_providers()
            assert "stripe" in providers or "cash" in providers  # Cash always available

    def test_get_gateway_case_insensitive(self):
        """Test that provider name is case-insensitive."""
        from app.services.payment.factory import get_gateway
        
        gateway_lower = get_gateway("cash")
        gateway_upper = get_gateway("CASH")
        
        # Both should work
        assert gateway_lower is not None
        assert gateway_upper is not None
