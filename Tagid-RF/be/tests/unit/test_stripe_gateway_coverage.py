import pytest
from unittest.mock import MagicMock, patch
from app.services.payment.stripe_gateway import StripeGateway
from app.services.payment.base import PaymentRequest, PaymentStatus

@pytest.fixture
def mock_stripe():
    """Mock the stripe library."""
    with patch("app.services.payment.stripe_gateway.stripe") as mock:
        yield mock

@pytest.fixture
def gateway(mock_stripe):
    """Create a StripeGateway instance with mocked dependencies."""
    # Force STRIPE_AVAILABLE to True for tests
    with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
        return StripeGateway(api_key="sk_test", webhook_secret="whsec_test")

@pytest.mark.asyncio
async def test_create_payment_success(gateway, mock_stripe):
    """Test successful payment intent creation."""
    intent = MagicMock()
    intent.id = "pi_123"
    intent.client_secret = "secret"
    intent.status = "requires_payment_method"
    mock_stripe.PaymentIntent.create.return_value = intent
    
    req = PaymentRequest(amount=100, currency="ILS", order_id="ord-1", customer_email="test@example.com")
    result = await gateway.create_payment(req)
    
    assert result.success
    assert result.payment_id == "pi_123"
    assert result.client_secret == "secret"
    mock_stripe.PaymentIntent.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_payment_error(gateway, mock_stripe):
    """Test payment creation error."""
    # Need to access the error class from the mock or actual stripe
    # Since we mocked the whole module, we need to setup the error class
    mock_stripe.error.StripeError = Exception
    mock_stripe.PaymentIntent.create.side_effect = Exception("Stripe Error")
    
    req = PaymentRequest(amount=100, currency="ILS", order_id="ord-1")
    result = await gateway.create_payment(req)
    
    assert not result.success
    assert "Stripe Error" in result.error

@pytest.mark.asyncio
async def test_confirm_payment(gateway, mock_stripe):
    """Test confirming payment."""
    intent = MagicMock()
    intent.id = "pi_123"
    intent.status = "succeeded"
    mock_stripe.PaymentIntent.confirm.return_value = intent
    
    result = await gateway.confirm_payment("pi_123", "pm_123")
    
    assert result.success
    assert result.status == PaymentStatus.COMPLETED

@pytest.mark.asyncio
async def test_get_payment_status(gateway, mock_stripe):
    """Test getting payment status."""
    intent = MagicMock()
    intent.id = "pi_123"
    intent.status = "processing"
    mock_stripe.PaymentIntent.retrieve.return_value = intent
    
    result = await gateway.get_payment_status("pi_123")
    
    assert result.success
    assert result.status == PaymentStatus.PROCESSING

@pytest.mark.asyncio
async def test_refund_payment(gateway, mock_stripe):
    """Test refunding payment."""
    refund = MagicMock()
    refund.id = "re_123"
    mock_stripe.Refund.create.return_value = refund
    
    result = await gateway.refund_payment("pi_123")
    
    assert result.success
    assert result.refund_id == "re_123"

def test_verify_webhook(gateway, mock_stripe):
    """Test webhook verification."""
    event = MagicMock()
    mock_stripe.Webhook.construct_event.return_value = event
    
    result = gateway.verify_webhook(b"payload", "sig")
    
    assert result == event
    mock_stripe.Webhook.construct_event.assert_called_once()
