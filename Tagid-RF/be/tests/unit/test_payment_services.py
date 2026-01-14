
import os
import sys
import pytest
import uuid
from unittest.mock import MagicMock, patch, AsyncMock
from app.services.payment.base import PaymentRequest, PaymentProvider, PaymentStatus, PaymentResult, RefundResult
from app.services.payment import factory

# Mock data
PAYMENT_REQUEST = PaymentRequest(
    order_id="order_123",
    amount=1000,
    currency="ILS",
    customer_email="test@example.com",
    metadata={"foo": "bar"}
)

class TestPaymentFactory:
    """Test the Payment Gateway Factory."""
    
    def test_get_gateway_caching(self):
        """Test that gateways are cached."""
        # Clear cache
        factory._gateways = {}
        
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_123"}):
            with patch("app.services.payment.stripe_gateway.stripe"): # Mock stripe lib
                g1 = factory.get_gateway("stripe")
                g2 = factory.get_gateway("stripe")
                assert g1 is g2
                assert g1.provider == PaymentProvider.STRIPE

    def test_get_gateway_tranzila(self):
        """Test creating Tranzila gateway."""
        factory._gateways = {}
        with patch.dict(os.environ, {"TRANZILA_TERMINAL": "term1", "TRANZILA_PASSWORD": "pass"}):
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
        with patch.dict(os.environ, {}, clear=True):
            # Ensure STRIPE_SECRET_KEY is missing
            with pytest.raises(ValueError, match="STRIPE_SECRET_KEY"):
                factory._create_stripe_gateway()

    def test_tranzila_config_error(self):
        """Test missing config raises error."""
        factory._gateways = {}
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TRANZILA_TERMINAL"):
                factory._create_tranzila_gateway()

    def test_get_available_providers(self):
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk", "TRANZILA_TERMINAL": "term"}):
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
        # We need to bypass factory to avoid caching issues or env checks if we want simple unit test
        from app.services.payment.stripe_gateway import StripeGateway
        # Force available
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
        assert result.payment_id == "pi_123"
        assert result.client_secret == "cs_123"
        mock_stripe.PaymentIntent.create.assert_called_once()
        assert mock_stripe.PaymentIntent.create.call_args[1]["amount"] == 1000

    @pytest.mark.asyncio
    async def test_create_payment_error(self, gateway, mock_stripe):
        mock_stripe.PaymentIntent.create.side_effect = Exception("Stripe Error") # Need specific StripeError usually, making generic for now or mocking StripeError
        # Actually stripe.error.StripeError is checked. We need to mock it.
        mock_stripe.error.StripeError = Exception
        
        result = await gateway.create_payment(PAYMENT_REQUEST)
        assert result.success is False
        assert "Stripe Error" in result.error

    @pytest.mark.asyncio
    async def test_confirm_payment(self, gateway, mock_stripe):
        mock_intent = MagicMock()
        mock_intent.status = "succeeded"
        mock_intent.id = "pi_123"
        mock_stripe.PaymentIntent.confirm.return_value = mock_intent
        
        result = await gateway.confirm_payment("pi_123")
        assert result.success is True
        assert result.status == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_refund_payment(self, gateway, mock_stripe):
        mock_refund = MagicMock()
        mock_refund.id = "re_123"
        mock_stripe.Refund.create.return_value = mock_refund
        
        result = await gateway.refund_payment("pi_123", 500)
        assert result.success is True
        assert result.refund_id == "re_123"


class TestTranzilaGateway:
    
    @pytest.fixture
    def gateway(self):
        from app.services.payment.tranzila import TranzilaGateway
        return TranzilaGateway("term1", "pass", use_redirect=True)

    @pytest.mark.asyncio
    async def test_create_redirect_payment(self, gateway):
        result = await gateway.create_payment(PAYMENT_REQUEST)
        assert result.success is True
        assert "secure5.tranzila.com" in result.redirect_url
        assert "sum=10.0" in result.redirect_url # 1000 cents / 100

    @pytest.mark.asyncio
    async def test_create_direct_payment_fail(self):
        from app.services.payment.tranzila import TranzilaGateway
        gateway = TranzilaGateway("term1", use_redirect=False)
        result = await gateway.create_payment(PAYMENT_REQUEST)
        assert result.success is False # Not implemented

    @pytest.mark.asyncio
    async def test_refund_payment_success(self, gateway):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_post.return_value = AsyncMock(text="Response=000&ConfirmationCode=123456")
            
            result = await gateway.refund_payment("order_123", 500)
            assert result.success is True
            assert result.refund_id == "123456"

    def test_verify_callback(self, gateway):
        params = {"Response": "000", "ConfirmationCode": "123", "orderId": "o1"}
        assert gateway.verify_callback(params) is True
        assert gateway.parse_callback(params).success is True


class TestCashGateway:
    
    @pytest.fixture
    def gateway(self):
        from app.services.payment.cash_gateway import CashGateway
        return CashGateway()

    @pytest.mark.asyncio
    async def test_create_payment(self, gateway):
        result = await gateway.create_payment(PAYMENT_REQUEST)
        assert result.success is True
        assert result.payment_id.startswith("cash_")
        assert result.status == PaymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_confirm_payment(self, gateway):
        result = await gateway.confirm_payment("cash_123")
        assert result.success is True
        assert result.status == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_refund_payment(self, gateway):
        result = await gateway.refund_payment("cash_123")
        assert result.success is True
        assert result.refund_id.startswith("refund_")
