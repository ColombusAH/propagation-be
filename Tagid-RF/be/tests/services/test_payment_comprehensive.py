"""
Comprehensive tests for Payment Gateway modules.
Covers base types, factory, and all gateway implementations.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


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
    from app.services.payment.factory import _gateways, get_gateway

    _gateways.clear()  # Clear cached gateways
    with pytest.raises(ValueError, match="Unknown payment provider"):
        get_gateway("unknown_provider")


def test_get_gateway_cash():
    """Test get_gateway returns CashGateway for 'cash' provider."""
    from app.services.payment.cash_gateway import CashGateway
    from app.services.payment.factory import _gateways, get_gateway

    _gateways.clear()
    gateway = get_gateway("cash")
    assert isinstance(gateway, CashGateway)


def test_get_gateway_caches_instance():
    """Test get_gateway returns cached instance on subsequent calls."""
    from app.services.payment.factory import _gateways, get_gateway

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
    from app.services.payment.base import PaymentProvider
    from app.services.payment.cash_gateway import CashGateway

    gateway = CashGateway()
    assert gateway.provider == PaymentProvider.CASH


@pytest.mark.asyncio
async def test_cash_gateway_create_payment():
    """Test CashGateway.create_payment creates pending payment."""
    from app.services.payment.base import PaymentRequest, PaymentStatus
    from app.services.payment.cash_gateway import CashGateway

    gateway = CashGateway()
    request = PaymentRequest(order_id="order-123", amount=1000)
    result = await gateway.create_payment(request)

    assert result.success is True
    assert result.payment_id.startswith("cash_")
    assert result.status == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_cash_gateway_confirm_payment():
    """Test CashGateway.confirm_payment completes payment."""
    from app.services.payment.base import PaymentStatus
    from app.services.payment.cash_gateway import CashGateway

    gateway = CashGateway()
    result = await gateway.confirm_payment("cash_12345678")

    assert result.success is True
    assert result.status == PaymentStatus.COMPLETED


@pytest.mark.asyncio
async def test_cash_gateway_get_status():
    """Test CashGateway.get_payment_status."""
    from app.services.payment.base import PaymentStatus
    from app.services.payment.cash_gateway import CashGateway

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
            from app.services.payment.base import PaymentProvider
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway(api_key="sk_test_123")
            assert gateway.provider == PaymentProvider.STRIPE


def test_stripe_gateway_map_status():
    """Test StripeGateway status mapping."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe"):
            from app.services.payment.base import PaymentStatus
            from app.services.payment.stripe_gateway import StripeGateway

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
            from app.services.payment.base import PaymentRequest
            from app.services.payment.stripe_gateway import StripeGateway

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
            from app.services.payment.base import PaymentRequest
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway(api_key="sk_test_123")
            request = PaymentRequest(order_id="order-123", amount=5000)
            result = await gateway.create_payment(request)

            assert result.success is False
            assert "API Error" in result.error


# --- Additional Stripe Tests ---
@pytest.mark.asyncio
async def test_stripe_gateway_confirm_payment():
    """Test StripeGateway.confirm_payment."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_CONFIRM"
    mock_intent.status = "succeeded"

    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.PaymentIntent.confirm.return_value = mock_intent
            from app.services.payment.base import PaymentStatus
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway(api_key="sk_test")
            result = await gateway.confirm_payment("pi_CONFIRM")

            assert result.success is True
            assert result.status == PaymentStatus.COMPLETED


@pytest.mark.asyncio
async def test_stripe_gateway_get_status():
    """Test StripeGateway.get_payment_status."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_STATUS"
    mock_intent.status = "processing"

    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.PaymentIntent.retrieve.return_value = mock_intent
            from app.services.payment.base import PaymentStatus
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway(api_key="sk_test")
            result = await gateway.get_payment_status("pi_STATUS")

            assert result.success is True
            assert result.status == PaymentStatus.PROCESSING


@pytest.mark.asyncio
async def test_stripe_gateway_refund():
    """Test StripeGateway.refund_payment."""
    mock_refund = MagicMock()
    mock_refund.id = "re_123"

    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.Refund.create.return_value = mock_refund
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway(api_key="sk_test")
            # Test full refund
            result = await gateway.refund_payment("pi_REFUND")
            assert result.success is True
            assert result.refund_id == "re_123"

            # Test partial refund
            await gateway.refund_payment("pi_REFUND", amount=500)
            mock_stripe.Refund.create.assert_called_with(payment_intent="pi_REFUND", amount=500)


def test_stripe_gateway_verify_webhook():
    """Test StripeGateway.verify_webhook."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.Webhook.construct_event.return_value = {"type": "payment_intent.succeeded"}
            from app.services.payment.stripe_gateway import StripeGateway

            # Fail without secret
            gateway_no_secret = StripeGateway(api_key="sk")
            with pytest.raises(ValueError):
                gateway_no_secret.verify_webhook(b"payload", "sig")

            # Success with secret
            gateway = StripeGateway(api_key="sk", webhook_secret="whsec_123")
            event = gateway.verify_webhook(b"payload", "sig")
            assert event["type"] == "payment_intent.succeeded"


# --- Tests for tranzila.py ---
def test_tranzila_gateway_provider():
    """Test TranzilaGateway provider type."""
    from app.services.payment.base import PaymentProvider
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test_term")
    assert gateway.provider == PaymentProvider.TRANZILA


@pytest.mark.asyncio
async def test_tranzila_create_redirect():
    """Test creating a redirect payment URL."""
    from app.services.payment.base import PaymentRequest, PaymentStatus
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test_term", terminal_password="pass")
    request = PaymentRequest(
        order_id="order_tz", amount=12300, currency="ILS", return_url="http://ret"
    )

    result = await gateway.create_payment(request)

    assert result.success is True
    assert result.status == PaymentStatus.PENDING
    assert "https://secure5.tranzila.com" in result.redirect_url
    assert "sum=123.0" in result.redirect_url
    assert "supplier=test_term" in result.redirect_url


@pytest.mark.asyncio
async def test_tranzila_create_direct_fails():
    """Test direct payment returns specific failure."""
    from app.services.payment.base import PaymentRequest
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="term", use_redirect=False)
    request = PaymentRequest(order_id="ord", amount=100)

    result = await gateway.create_payment(request)
    assert result.success is False
    assert "tokenized card" in result.error


@pytest.mark.asyncio
async def test_tranzila_refund_success():
    """Test successful refund via HTTP."""
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="term", terminal_password="pass")

    # Mock httpx response
    mock_resp = MagicMock()
    # Response=000 indicates success
    mock_resp.text = "Response=000&ConfirmationCode=98765"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await gateway.refund_payment("pay_123", amount=500)

        assert result.success is True
        assert result.refund_id == "98765"
        mock_post.assert_awaited()


@pytest.mark.asyncio
async def test_tranzila_refund_failure():
    """Test failed refund."""
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="term")
    mock_resp = MagicMock()
    mock_resp.text = "Response=001&error=Failed"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = await gateway.refund_payment("pay_123")
        assert result.success is False


def test_tranzila_verify_callback():
    """Test callback verification logic."""
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway("term")

    # Valid
    assert gateway.verify_callback({"Response": "000", "ConfirmationCode": "123"}) is True
    # Invalid response
    assert gateway.verify_callback({"Response": "001", "ConfirmationCode": "123"}) is False
    # Missing confirmation
    assert gateway.verify_callback({"Response": "000"}) is False


def test_tranzila_parse_callback():
    """Test callback parsing."""
    from app.services.payment.base import PaymentStatus
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway("term")

    # Success case
    params = {"Response": "000", "ConfirmationCode": "CONF123", "orderId": "ORDER1"}
    res = gateway.parse_callback(params)
    assert res.success is True
    assert res.payment_id == "ORDER1"
    assert res.external_id == "CONF123"
    assert res.status == PaymentStatus.COMPLETED

    # Failure case
    fail_params = {"Response": "005", "orderId": "ORDER2"}
    res_fail = gateway.parse_callback(fail_params)
    assert res_fail.success is False
    assert res_fail.status == PaymentStatus.FAILED


# --- Error Path Tests ---
def test_stripe_gateway_import_error():
    """Test behavior when Stripe is not installed."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", False):
        from app.services.payment.stripe_gateway import StripeGateway

        with pytest.raises(RuntimeError):
            StripeGateway("key")


@pytest.mark.asyncio
async def test_stripe_gateway_confirm_error():
    """Test Stripe gateway confirm error handling."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.error.StripeError = Exception
            mock_stripe.PaymentIntent.confirm.side_effect = Exception("Confirm Error")
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway("key")
            result = await gateway.confirm_payment("pi_123")
            assert result.success is False
            assert "Confirm Error" in result.error


@pytest.mark.asyncio
async def test_stripe_gateway_status_error():
    """Test Stripe gateway status error handling."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.error.StripeError = Exception
            mock_stripe.PaymentIntent.retrieve.side_effect = Exception("Status Error")
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway("key")
            result = await gateway.get_payment_status("pi_123")
            assert result.success is False
            assert "Status Error" in result.error


@pytest.mark.asyncio
async def test_stripe_gateway_refund_exception():
    """Test Stripe gateway refund error handling."""
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_stripe.error.StripeError = Exception
            mock_stripe.Refund.create.side_effect = Exception("Refund Error")
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway("key")
            result = await gateway.refund_payment("pi_123")
            assert result.success is False
            assert "Refund Error" in result.error


@pytest.mark.asyncio
async def test_tranzila_refund_exception_handling():
    """Test Tranzila refund generic exception."""
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway("term")
    with patch("httpx.AsyncClient.post", side_effect=Exception("Network Error")):
        result = await gateway.refund_payment("pay_123")
        assert result.success is False
        assert "Network Error" in result.error
