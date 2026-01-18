"""
Standardized tests for Payment Services.
"""
import os
import sys
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.payment import factory
from app.services.payment.base import (
    PaymentProvider,
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
    RefundResult,
)

# Mock data
PAYMENT_REQUEST = PaymentRequest(
    order_id="order_123",
    amount=1000,
    currency="ILS",
    customer_email="test@example.com",
    metadata={"foo": "bar"},
)


class TestPaymentFactory:
    """Test the Payment Gateway Factory."""

    def test_get_gateway_caching(self):
        """Test that gateways are cached."""
        factory._gateways = {}
        # Patch BOTH the settings in the module and the dependency if any
        with patch.object(factory, "settings") as mock_settings:
            mock_settings.STRIPE_SECRET_KEY = "sk_test_123"
            mock_settings.STRIPE_WEBHOOK_SECRET = "whsec_123"
            
            with patch("app.services.payment.stripe_gateway.stripe"):
                g1 = factory.get_gateway("stripe")
                g2 = factory.get_gateway("stripe")
                assert g1 is g2

    def test_get_gateway_tranzila(self):
        """Test creating Tranzila gateway."""
        factory._gateways = {}
        with patch.object(factory, "settings") as mock_settings:
            mock_settings.TRANZILA_TERMINAL_NAME = "term1"
            mock_settings.TRANZILA_API_KEY = "pass"
            
            g = factory.get_gateway("tranzila")
            assert g.provider == PaymentProvider.TRANZILA

    def test_get_gateway_cash(self):
        """Test creating Cash gateway."""
        factory._gateways = {}
        g = factory.get_gateway("cash")
        assert g.provider == PaymentProvider.CASH

    def test_get_gateway_invalid(self):
        """Test unknown provider."""
        with pytest.raises(ValueError, match="Unknown payment provider"):
            factory.get_gateway("unknown")

    def test_stripe_config_error(self):
        """Test missing config raises error."""
        factory._gateways = {}
        # Use patch.object to ensure it replaces the exact reference used by the function
        with patch.object(factory, "settings", MagicMock()) as mock_settings:
            mock_settings.STRIPE_SECRET_KEY = None
            with pytest.raises(ValueError, match="STRIPE_SECRET_KEY"):
                factory._create_stripe_gateway()

    def test_tranzila_config_error(self):
        """Test missing config raises error."""
        factory._gateways = {}
        with patch.object(factory, "settings", MagicMock()) as mock_settings:
            mock_settings.TRANZILA_TERMINAL_NAME = None
            with pytest.raises(ValueError, match="TRANZILA_TERMINAL_NAME"):
                factory._create_tranzila_gateway()

    def test_get_available_providers(self):
        with patch("os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda k: "val" if k in ["STRIPE_SECRET_KEY", "TRANZILA_TERMINAL"] else None
            providers = factory.get_available_providers()
            assert "stripe" in providers
            assert "tranzila" in providers
            assert "cash" in providers


class TestStripeGateway:
    """Test Stripe Gateway logic."""

    @pytest.fixture
    def mock_stripe(self):
        with patch("app.services.payment.stripe_gateway.stripe") as mock:
            yield mock

    @pytest.fixture
    def gateway(self, mock_stripe):
        from app.services.payment.stripe_gateway import StripeGateway
        with patch("app.services.payment.stripe_gateway.STRIPE_AVAILABLE", True):
            return StripeGateway(api_key="sk_test", webhook_secret="wh_sec")

    @pytest.mark.asyncio
    async def test_create_payment_success(self, gateway, mock_stripe):
        mock_intent = MagicMock()
        mock_intent.id = "pi_123"
        mock_intent.client_secret = "cs_123"
        mock_intent.status = "requires_payment_method"
        mock_stripe.PaymentIntent.create.return_value = mock_intent

        result = await gateway.create_payment(PAYMENT_REQUEST)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_create_payment_error(self, gateway, mock_stripe):
        mock_stripe.PaymentIntent.create.side_effect = Exception("Stripe Error")
        mock_stripe.error.StripeError = Exception
        result = await gateway.create_payment(PAYMENT_REQUEST)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_confirm_payment(self, gateway, mock_stripe):
        mock_intent = MagicMock()
        mock_intent.status = "succeeded"
        mock_intent.id = "pi_123"
        mock_stripe.PaymentIntent.confirm.return_value = mock_intent
        result = await gateway.confirm_payment("pi_123")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_refund_payment(self, gateway, mock_stripe):
        mock_refund = MagicMock()
        mock_refund.id = "re_123"
        mock_stripe.Refund.create.return_value = mock_refund
        result = await gateway.refund_payment("pi_123", 500)
        assert result.success is True
