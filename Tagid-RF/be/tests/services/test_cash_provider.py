"""
Tests for Cash Provider Service.
"""

import pytest

from app.services.cash_provider import CashProvider
from app.services.payment_provider import PaymentStatus


class TestCashProvider:
    """Tests for CashProvider."""

    @pytest.fixture
    def provider(self):
        """Create CashProvider instance."""
        return CashProvider()

    def test_provider_init(self, provider):
        """Test provider initialization."""
        assert provider is not None
        assert hasattr(provider, "pending_payments")
        assert provider.pending_payments == {}

    @pytest.mark.asyncio
    async def test_create_payment_intent(self, provider):
        """Test creating cash payment intent."""
        result = await provider.create_payment_intent(amount=1000, currency="ILS")

        assert result is not None
        assert "payment_id" in result
        assert result["status"] == PaymentStatus.PENDING
        assert result["payment_id"].startswith("cash_")

    @pytest.mark.asyncio
    async def test_full_payment_flow(self, provider):
        """Test complete payment flow: create -> confirm."""
        # Create payment
        create_result = await provider.create_payment_intent(
            amount=2000, currency="ILS", metadata={"order_id": "order_123"}
        )
        payment_id = create_result["payment_id"]

        # Verify payment exists
        assert payment_id in provider.pending_payments

        # Confirm payment
        confirm_result = await provider.confirm_payment(payment_id)

        assert confirm_result["status"] == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_refund_flow(self, provider):
        """Test refund flow: create -> confirm -> refund."""
        # Create and confirm payment
        create_result = await provider.create_payment_intent(1500, "ILS")
        payment_id = create_result["payment_id"]
        await provider.confirm_payment(payment_id)

        # Refund
        refund_result = await provider.refund_payment(payment_id)

        assert refund_result["status"] == PaymentStatus.REFUNDED
        assert refund_result["amount"] == 1500

    @pytest.mark.asyncio
    async def test_cancel_pending_payment(self, provider):
        """Test cancelling a pending payment."""
        create_result = await provider.create_payment_intent(500, "ILS")
        payment_id = create_result["payment_id"]

        # Cancel before confirmation
        cancel_result = await provider.cancel_payment(payment_id)

        assert cancel_result["status"] == PaymentStatus.FAILED

    @pytest.mark.asyncio
    async def test_get_payment_status(self, provider):
        """Test getting payment status."""
        create_result = await provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]

        status = await provider.get_payment_status(payment_id)

        assert status == PaymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_confirm_nonexistent_payment(self, provider):
        """Test confirming non-existent payment raises error."""
        with pytest.raises(ValueError, match="not found"):
            await provider.confirm_payment("nonexistent_id")
