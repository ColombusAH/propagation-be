"""
Extended tests for Stripe Provider Service.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.payment_provider import PaymentStatus
from app.services.stripe_provider import StripeProvider


class TestStripeProviderExtended:
    """Extended tests for StripeProvider."""

    @pytest.fixture
    def provider(self):
        """Create StripeProvider instance."""
        with patch("stripe.api_key", "sk_test_xxx"):
            return StripeProvider()

    def test_provider_init(self, provider):
        """Test provider initialization."""
        assert provider is not None

    @pytest.mark.asyncio
    async def test_create_payment_intent_mock(self, provider):
        """Test creating payment intent with mocked Stripe."""
        with patch("stripe.PaymentIntent.create") as mock_create:
            mock_create.return_value = MagicMock(
                id="pi_test123", client_secret="cs_test", status="requires_payment_method"
            )

            result = await provider.create_payment_intent(amount=1000, currency="ILS")

            assert result is not None
            assert "payment_id" in result

    @pytest.mark.asyncio
    async def test_confirm_payment_mock(self, provider):
        """Test confirming payment with mocked Stripe."""
        with patch("stripe.PaymentIntent.confirm") as mock_confirm:
            mock_confirm.return_value = MagicMock(id="pi_test123", status="succeeded")

            result = await provider.confirm_payment(
                payment_id="pi_test123", payment_method_id="pm_test"
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_get_payment_status_mock(self, provider):
        """Test getting payment status with mocked Stripe."""
        with patch("stripe.PaymentIntent.retrieve") as mock_retrieve:
            mock_retrieve.return_value = MagicMock(status="succeeded")

            status = await provider.get_payment_status("pi_test123")

            assert status is not None

    @pytest.mark.asyncio
    async def test_refund_payment_mock(self, provider):
        """Test refunding payment with mocked Stripe."""
        with patch("stripe.Refund.create") as mock_refund:
            mock_refund.return_value = MagicMock(id="re_test123", status="succeeded")

            result = await provider.refund_payment("pi_test123")

            assert result is not None
