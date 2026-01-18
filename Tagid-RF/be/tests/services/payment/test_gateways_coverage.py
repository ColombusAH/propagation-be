"""
Comprehensive tests for CashGateway and StripeGateway.
Covers all methods of the payment gateway implementations.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestCashGateway:
    """Tests for CashGateway."""

    @pytest.fixture
    def gateway(self):
        """Create CashGateway instance."""
        from app.services.payment.cash_gateway import CashGateway

        return CashGateway()

    def test_provider_property(self, gateway):
        """Test provider property returns CASH."""
        from app.services.payment.base import PaymentProvider

        assert gateway.provider == PaymentProvider.CASH

    @pytest.mark.asyncio
    async def test_create_payment(self, gateway):
        """Test creating a cash payment."""
        from app.services.payment.base import PaymentRequest, PaymentStatus

        request = PaymentRequest(order_id="order-123", amount=1000, currency="ILS")

        result = await gateway.create_payment(request)

        assert result.success is True
        assert result.payment_id.startswith("cash_")
        assert result.status == PaymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_confirm_payment(self, gateway):
        """Test confirming a cash payment."""
        from app.services.payment.base import PaymentStatus

        result = await gateway.confirm_payment("cash_12345")

        assert result.success is True
        assert result.status == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_payment_status(self, gateway):
        """Test getting payment status."""
        from app.services.payment.base import PaymentStatus

        result = await gateway.get_payment_status("cash_12345")

        assert result.success is True
        assert result.status == PaymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_refund_payment(self, gateway):
        """Test refunding a cash payment."""
        result = await gateway.refund_payment("cash_12345", 500)

        assert result.success is True
        assert result.refund_id.startswith("refund_")

    @pytest.mark.asyncio
    async def test_refund_payment_full(self, gateway):
        """Test full refund."""
        result = await gateway.refund_payment("cash_12345")

        assert result.success is True


class TestStripeGateway:
    """Tests for StripeGateway."""

    @pytest.fixture
    def gateway(self):
        """Create StripeGateway instance with mocked stripe."""
        with (
            patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True),
            patch("app.services.payment.stripe_gateway.stripe"),
        ):
            from app.services.payment.stripe_gateway import StripeGateway

            return StripeGateway(api_key="sk_test_123", webhook_secret="whsec_test")

    def test_provider_property(self, gateway):
        """Test provider property returns STRIPE."""
        from app.services.payment.base import PaymentProvider

        assert gateway.provider == PaymentProvider.STRIPE

    @pytest.mark.asyncio
    async def test_create_payment(self, gateway):
        """Test creating a Stripe payment."""
        from app.services.payment.base import PaymentRequest

        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_intent = MagicMock()
            mock_intent.id = "pi_12345"
            mock_intent.client_secret = "secret_123"
            mock_intent.status = "requires_payment_method"
            mock_stripe.PaymentIntent.create.return_value = mock_intent

            request = PaymentRequest(order_id="order-123", amount=1000, currency="ILS")

            result = await gateway.create_payment(request)

            assert result.success is True
            assert result.payment_id == "pi_12345"

    @pytest.mark.asyncio
    async def test_confirm_payment(self, gateway):
        """Test confirming a Stripe payment."""
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_intent = MagicMock()
            mock_intent.id = "pi_12345"
            mock_intent.status = "succeeded"
            mock_stripe.PaymentIntent.confirm.return_value = mock_intent

            result = await gateway.confirm_payment("pi_12345", "pm_card")

            assert result.success is True

    @pytest.mark.asyncio
    async def test_get_payment_status(self, gateway):
        """Test getting Stripe payment status."""
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_intent = MagicMock()
            mock_intent.id = "pi_12345"
            mock_intent.status = "succeeded"
            mock_stripe.PaymentIntent.retrieve.return_value = mock_intent

            result = await gateway.get_payment_status("pi_12345")

            assert result.success is True

    @pytest.mark.asyncio
    async def test_refund_payment(self, gateway):
        """Test refunding a Stripe payment."""
        with patch("app.services.payment.stripe_gateway.stripe") as mock_stripe:
            mock_refund = MagicMock()
            mock_refund.id = "re_12345"
            mock_stripe.Refund.create.return_value = mock_refund

            result = await gateway.refund_payment("pi_12345", 500)

            assert result.success is True
            assert result.refund_id == "re_12345"

    def test_map_status(self, gateway):
        """Test status mapping."""
        from app.services.payment.base import PaymentStatus

        assert gateway._map_status("succeeded") == PaymentStatus.COMPLETED
        assert gateway._map_status("processing") == PaymentStatus.PROCESSING
        assert gateway._map_status("requires_payment_method") == PaymentStatus.PENDING
        assert gateway._map_status("canceled") == PaymentStatus.FAILED

    def test_verify_webhook_no_secret(self):
        """Test webhook verification without secret."""
        with (
            patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True),
            patch("app.services.payment.stripe_gateway.stripe"),
        ):
            from app.services.payment.stripe_gateway import StripeGateway

            gateway = StripeGateway(api_key="sk_test_123")  # No webhook secret

            with pytest.raises(ValueError, match="Webhook secret not configured"):
                gateway.verify_webhook(b"payload", "signature")


class TestPaymentProviderEnum:
    """Tests for PaymentStatus enum from payment_provider.py."""

    def test_payment_status_values(self):
        """Test PaymentStatus enum values."""
        from app.services.payment_provider import PaymentStatus

        assert PaymentStatus.PENDING == "PENDING"
        assert PaymentStatus.PROCESSING == "PROCESSING"
        assert PaymentStatus.COMPLETED == "COMPLETED"
        assert PaymentStatus.FAILED == "FAILED"
        assert PaymentStatus.REFUNDED == "REFUNDED"
