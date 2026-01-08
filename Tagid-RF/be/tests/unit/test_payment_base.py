"""
Unit tests for payment gateway base classes and types.
"""

import pytest
from unittest.mock import AsyncMock


@pytest.mark.unit
class TestPaymentProvider:
    """Tests for PaymentProvider enum."""

    def test_payment_provider_values(self):
        """Test PaymentProvider enum values."""
        from app.services.payment.base import PaymentProvider
        
        assert PaymentProvider.STRIPE.value == "stripe"
        assert PaymentProvider.TRANZILA.value == "tranzila"
        assert PaymentProvider.CASH.value == "cash"

    def test_payment_provider_is_string_enum(self):
        """Test PaymentProvider is string enum."""
        from app.services.payment.base import PaymentProvider
        
        assert isinstance(PaymentProvider.STRIPE, str)
        assert PaymentProvider.STRIPE == "stripe"


@pytest.mark.unit
class TestPaymentStatus:
    """Tests for PaymentStatus enum."""

    def test_payment_status_values(self):
        """Test PaymentStatus enum values."""
        from app.services.payment.base import PaymentStatus
        
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.PROCESSING.value == "processing"
        assert PaymentStatus.COMPLETED.value == "completed"
        assert PaymentStatus.FAILED.value == "failed"
        assert PaymentStatus.REFUNDED.value == "refunded"

    def test_payment_status_all_values(self):
        """Test all payment statuses exist."""
        from app.services.payment.base import PaymentStatus
        
        statuses = list(PaymentStatus)
        assert len(statuses) == 5


@pytest.mark.unit
class TestPaymentRequest:
    """Tests for PaymentRequest model."""

    def test_payment_request_full(self):
        """Test PaymentRequest with all fields."""
        from app.services.payment.base import PaymentRequest
        
        request = PaymentRequest(
            order_id="order123",
            amount=15000,
            currency="ILS",
            customer_email="test@example.com",
            customer_name="Test User",
            return_url="https://example.com/return",
            metadata={"key": "value"}
        )
        
        assert request.order_id == "order123"
        assert request.amount == 15000
        assert request.currency == "ILS"
        assert request.customer_email == "test@example.com"

    def test_payment_request_minimal(self):
        """Test PaymentRequest with required fields only."""
        from app.services.payment.base import PaymentRequest
        
        request = PaymentRequest(
            order_id="order123",
            amount=5000
        )
        
        assert request.order_id == "order123"
        assert request.amount == 5000
        assert request.currency == "ILS"  # Default
        assert request.customer_email is None

    def test_payment_request_currency_default(self):
        """Test PaymentRequest default currency is ILS."""
        from app.services.payment.base import PaymentRequest
        
        request = PaymentRequest(order_id="123", amount=1000)
        assert request.currency == "ILS"


@pytest.mark.unit
class TestPaymentResult:
    """Tests for PaymentResult model."""

    def test_payment_result_success(self):
        """Test successful PaymentResult."""
        from app.services.payment.base import PaymentResult, PaymentStatus
        
        result = PaymentResult(
            success=True,
            payment_id="pay123",
            external_id="ext123",
            status=PaymentStatus.COMPLETED
        )
        
        assert result.success is True
        assert result.payment_id == "pay123"
        assert result.status == PaymentStatus.COMPLETED

    def test_payment_result_failure(self):
        """Test failed PaymentResult."""
        from app.services.payment.base import PaymentResult, PaymentStatus
        
        result = PaymentResult(
            success=False,
            payment_id="pay123",
            error="Card declined",
            status=PaymentStatus.FAILED
        )
        
        assert result.success is False
        assert result.error == "Card declined"
        assert result.status == PaymentStatus.FAILED

    def test_payment_result_default_status(self):
        """Test PaymentResult default status is PENDING."""
        from app.services.payment.base import PaymentResult, PaymentStatus
        
        result = PaymentResult(success=True, payment_id="pay123")
        assert result.status == PaymentStatus.PENDING


@pytest.mark.unit
class TestRefundResult:
    """Tests for RefundResult model."""

    def test_refund_result_success(self):
        """Test successful RefundResult."""
        from app.services.payment.base import RefundResult
        
        result = RefundResult(
            success=True,
            refund_id="ref123"
        )
        
        assert result.success is True
        assert result.refund_id == "ref123"
        assert result.error is None

    def test_refund_result_failure(self):
        """Test failed RefundResult."""
        from app.services.payment.base import RefundResult
        
        result = RefundResult(
            success=False,
            error="Refund not allowed"
        )
        
        assert result.success is False
        assert result.refund_id is None
        assert result.error == "Refund not allowed"


@pytest.mark.unit
class TestPaymentGateway:
    """Tests for PaymentGateway abstract base class."""

    def test_payment_gateway_is_abstract(self):
        """Test PaymentGateway cannot be instantiated directly."""
        from app.services.payment.base import PaymentGateway
        
        with pytest.raises(TypeError):
            PaymentGateway()

    def test_payment_gateway_has_required_methods(self):
        """Test PaymentGateway has required abstract methods."""
        from app.services.payment.base import PaymentGateway
        import inspect
        
        methods = inspect.getmembers(PaymentGateway, predicate=inspect.isfunction)
        method_names = [m[0] for m in methods]
        
        assert "create_payment" in method_names
        assert "confirm_payment" in method_names
        assert "get_payment_status" in method_names
        assert "refund_payment" in method_names
