"""
Tests for Stripe Payment Provider.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.payment_provider import PaymentStatus
from app.services.stripe_provider import StripeProvider


@pytest.fixture
def stripe_provider():
    """Create StripeProvider with mocked settings."""
    with patch("app.services.stripe_provider.settings") as mock_settings:
        mock_settings.STRIPE_SECRET_KEY = "sk_test_123"
        mock_settings.STRIPE_PUBLISHABLE_KEY = "pk_test_123"

        with patch("app.services.stripe_provider.stripe"):
            provider = StripeProvider()
            return provider


@pytest.mark.asyncio
async def test_create_payment_intent_success(stripe_provider):
    """Test successful payment intent creation."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_123"
    mock_intent.client_secret = "secret_123"

    with patch("stripe.PaymentIntent.create", return_value=mock_intent):
        result = await stripe_provider.create_payment_intent(amount=1000, currency="USD")

        assert result["payment_id"] == "pi_123"
        assert result["status"] == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_create_payment_intent_with_metadata(stripe_provider):
    """Test payment intent with metadata."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_456"
    mock_intent.client_secret = "secret_456"

    with patch("stripe.PaymentIntent.create", return_value=mock_intent):
        result = await stripe_provider.create_payment_intent(
            amount=2000, currency="ILS", metadata={"order_id": "order_123"}
        )

        assert result["payment_id"] == "pi_456"


@pytest.mark.asyncio
async def test_confirm_payment_with_method(stripe_provider):
    """Test confirming payment with payment method."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_123"
    mock_intent.status = "succeeded"
    mock_intent.payment_method = "pm_123"

    with patch("stripe.PaymentIntent.confirm", return_value=mock_intent):
        result = await stripe_provider.confirm_payment(
            payment_id="pi_123", payment_method_id="pm_123"
        )

        assert result["status"] == PaymentStatus.COMPLETED


@pytest.mark.asyncio
async def test_confirm_payment_retrieve_only(stripe_provider):
    """Test confirm payment when just retrieving status."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_123"
    mock_intent.status = "requires_payment_method"
    mock_intent.payment_method = None

    with patch("stripe.PaymentIntent.retrieve", return_value=mock_intent):
        result = await stripe_provider.confirm_payment(payment_id="pi_123")

        assert result["status"] == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_refund_payment_full(stripe_provider):
    """Test full refund."""
    mock_refund = MagicMock()
    mock_refund.id = "re_123"
    mock_refund.amount = 1000

    with patch("stripe.Refund.create", return_value=mock_refund):
        result = await stripe_provider.refund_payment(payment_id="pi_123")

        assert result["status"] == PaymentStatus.REFUNDED


@pytest.mark.asyncio
async def test_refund_payment_partial(stripe_provider):
    """Test partial refund."""
    mock_refund = MagicMock()
    mock_refund.id = "re_456"
    mock_refund.amount = 500

    with patch("stripe.Refund.create", return_value=mock_refund):
        result = await stripe_provider.refund_payment(payment_id="pi_123", amount=500)

        assert result["refund_id"] == "re_456"
        assert result["amount"] == 500


@pytest.mark.asyncio
async def test_get_payment_status(stripe_provider):
    """Test getting payment status."""
    mock_intent = MagicMock()
    mock_intent.status = "succeeded"

    with patch("stripe.PaymentIntent.retrieve", return_value=mock_intent):
        status = await stripe_provider.get_payment_status("pi_123")

        assert status == PaymentStatus.COMPLETED


@pytest.mark.asyncio
async def test_cancel_payment(stripe_provider):
    """Test payment cancellation."""
    mock_intent = MagicMock()
    mock_intent.id = "pi_123"

    with patch("stripe.PaymentIntent.cancel", return_value=mock_intent):
        result = await stripe_provider.cancel_payment("pi_123")

        assert result["status"] == PaymentStatus.FAILED


def test_map_stripe_status(stripe_provider):
    """Test status mapping."""
    assert stripe_provider._map_stripe_status("succeeded") == PaymentStatus.COMPLETED
    assert stripe_provider._map_stripe_status("canceled") == PaymentStatus.FAILED
    assert stripe_provider._map_stripe_status("processing") == PaymentStatus.PROCESSING
    assert stripe_provider._map_stripe_status("requires_payment_method") == PaymentStatus.PENDING
    assert stripe_provider._map_stripe_status("unknown_status") == PaymentStatus.FAILED


@pytest.mark.asyncio
async def test_create_payment_intent_stripe_error(stripe_provider):
    """Test handling Stripe error."""
    import stripe

    with patch("stripe.PaymentIntent.create", side_effect=stripe.error.StripeError("Test error")):
        with pytest.raises(ValueError, match="Failed to create payment intent"):
            await stripe_provider.create_payment_intent(1000, "USD")
