"""
Comprehensive tests for Payment Gateway modules.
Covers base types, factory, and all gateway implementations.
"""
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


# --- Tests for base.py ---
def test_payment_provider_enum():
    """Test PaymentProvider enum values."""
    from app.services.payment.base import PaymentProvider

    assert PaymentProvider.STRIPE == "stripe"
    assert PaymentProvider.TRANZILA == "tranzila"
    assert PaymentProvider.CASH == "cash"


def test_payment_status_enum():
    """Test PaymentStatus enum values."""
    from app.services.payment.base import PaymentStatus

    assert PaymentStatus.PENDING == "pending"
    assert PaymentStatus.COMPLETED == "completed"
    assert PaymentStatus.FAILED == "failed"
    assert PaymentStatus.REFUNDED == "refunded"


def test_payment_request_model():
    """Test PaymentRequest model creation."""
    from app.services.payment.base import PaymentRequest

    request = PaymentRequest(order_id="order-123", amount=5000, currency="ILS")
    assert request.order_id == "order-123"
    assert request.amount == 5000
    assert request.currency == "ILS"


def test_payment_result_model():
    """Test PaymentResult model creation."""
    from app.services.payment.base import PaymentResult, PaymentStatus

    result = PaymentResult(success=True, payment_id="pay-123", status=PaymentStatus.COMPLETED)
    assert result.success is True
    assert result.payment_id == "pay-123"
    assert result.status == PaymentStatus.COMPLETED


def test_refund_result_model():
    """Test RefundResult model creation."""
    from app.services.payment.base import RefundResult

    result = RefundResult(success=True, refund_id="ref-123")
    assert result.success is True
    assert result.refund_id == "ref-123"


# --- Tests for factory.py ---
def test_get_gateway_unknown_provider():
    """Test get_gateway raises error for unknown provider."""
    from app.services.payment.factory import get_gateway, _gateways

    _gateways.clear()  # Clear cached gateways
    with pytest.raises(ValueError, match="Unknown payment provider"):
        get_gateway("unknown_provider")


def test_get_gateway_cash():
    """Test get_gateway returns CashGateway for 'cash' provider."""
    from app.services.payment.factory import get_gateway, _gateways
    from app.services.payment.cash_gateway import CashGateway

    _gateways.clear()
    gateway = get_gateway("cash")
    assert isinstance(gateway, CashGateway)


def test_get_gateway_caches_instance():
    """Test get_gateway returns cached instance on subsequent calls."""
    from app.services.payment.factory import get_gateway, _gateways

    _gateways.clear()
    gateway1 = get_gateway("cash")
    gateway2 = get_gateway("cash")
    assert gateway1 is gateway2


def test_get_available_providers_cash_always():
    """Test get_available_providers always includes cash."""
    from app.services.payment.factory import get_available_providers

    providers = get_available_providers()
    assert "cash" in providers


@patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_123"}, clear=False)
def test_get_available_providers_with_stripe():
    """Test get_available_providers includes stripe when configured."""
    from app.services.payment.factory import get_available_providers

    providers = get_available_providers()
    assert "stripe" in providers
    assert "cash" in providers


# --- Tests for cash_gateway.py ---
@pytest.mark.asyncio
async def test_cash_gateway_provider():
    """Test CashGateway returns correct provider."""
    from app.services.payment.cash_gateway import CashGateway
    from app.services.payment.base import PaymentProvider

    gateway = CashGateway()
    assert gateway.provider == PaymentProvider.CASH


@pytest.mark.asyncio
async def test_cash_gateway_create_payment():
    """Test CashGateway.create_payment creates pending payment."""
    from app.services.payment.cash_gateway import CashGateway
    from app.services.payment.base import PaymentRequest, PaymentStatus

    gateway = CashGateway()
    request = PaymentRequest(order_id="order-123", amount=1000)
    result = await gateway.create_payment(request)

    assert result.success is True
    assert result.payment_id.startswith("cash_")
    assert result.status == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_cash_gateway_confirm_payment():
    """Test CashGateway.confirm_payment completes payment."""
    from app.services.payment.cash_gateway import CashGateway
    from app.services.payment.base import PaymentStatus

    gateway = CashGateway()
    result = await gateway.confirm_payment("cash_12345678")

    assert result.success is True
    assert result.status == PaymentStatus.COMPLETED


@pytest.mark.asyncio
async def test_cash_gateway_get_status():
    """Test CashGateway.get_payment_status."""
    from app.services.payment.cash_gateway import CashGateway
    from app.services.payment.base import PaymentStatus

    gateway = CashGateway()
    result = await gateway.get_payment_status("cash_12345678")

    assert result.success is True
    assert result.status == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_cash_gateway_refund():
    """Test CashGateway.refund_payment."""
    from app.services.payment.cash_gateway import CashGateway

    gateway = CashGateway()
    result = await gateway.refund_payment("cash_12345678")

    assert result.success is True
    assert result.refund_id.startswith("refund_")


# --- Tests for stripe_gateway.py ---
def test_stripe_gateway_provider():
    """Test StripeGateway returns correct provider."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe"):
            from app.services.payment.stripe_gateway import StripeGateway
            from app.services.payment.base import PaymentProvider

            gateway = StripeGateway(api_key="sk_test_123")
            assert gateway.provider == PaymentProvider.STRIPE


def test_stripe_gateway_map_status():
    """Test StripeGateway status mapping."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe"):
            from app.services.payment.stripe_gateway import StripeGateway
            from app.services.payment.base import PaymentStatus

            gateway = StripeGateway(api_key="sk_test_123")
            assert gateway._map_status("succeeded") == PaymentStatus.COMPLETED
            assert gateway._map_status("processing") == PaymentStatus.PROCESSING
            assert gateway._map_status("canceled") == PaymentStatus.FAILED
            assert gateway._map_status("unknown") == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_stripe_gateway_create_payment_success():
    """Test StripeGateway.create_payment success."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_test_123"
    mock_intent.client_secret = "secret_123"
    mock_intent.status = "requires_payment_method"

    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.PaymentIntent.create.return_value = mock_intent
            from app.services.payment.stripe_gateway import StripeGateway
            from app.services.payment.base import PaymentRequest

            gateway = StripeGateway(api_key="sk_test_123")
            request = PaymentRequest(order_id="order-123", amount=5000)
            result = await gateway.create_payment(request)

            assert result.success is True
            assert result.payment_id == "pi_test_123"
            assert result.client_secret == "secret_123"


@pytest.mark.asyncio
async def test_stripe_gateway_create_payment_error():
    """Test StripeGateway.create_payment error handling."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.error.StripeError = Exception
            mock_stripe.PaymentIntent.create.side_effect = Exception("API Error")
            from app.services.payment.stripe_gateway import StripeGateway
            from app.services.payment.base import PaymentRequest

            gateway = StripeGateway(api_key="sk_test_123")
            request = PaymentRequest(order_id="order-123", amount=5000)
            result = await gateway.create_payment(request)

            assert result.success is False
            assert "API Error" in result.error
