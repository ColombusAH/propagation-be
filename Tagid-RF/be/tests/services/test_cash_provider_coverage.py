"""
Comprehensive tests for CashProvider service.
Covers: create_payment_intent, confirm_payment, refund_payment, get_payment_status, cancel_payment
"""

import pytest
from app.services.cash_provider import CashProvider
from app.services.payment_provider import PaymentStatus


class TestCashProvider:
    """Tests for CashProvider service."""

    @pytest.fixture
    def provider(self):
        """Create a fresh CashProvider instance."""
        return CashProvider()

    @pytest.mark.asyncio
    async def test_create_payment_intent(self, provider):
        """Test creating a cash payment intent."""
        result = await provider.create_payment_intent(1000, "ILS", {"note": "test"})
        
        assert "payment_id" in result
        assert result["status"] == PaymentStatus.PENDING
        assert result["external_id"] == result["payment_id"]
        assert result["client_secret"] is None

    @pytest.mark.asyncio
    async def test_create_payment_intent_without_metadata(self, provider):
        """Test creating payment intent without metadata."""
        result = await provider.create_payment_intent(500, "ILS")
        
        assert result["status"] == PaymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_confirm_payment_success(self, provider):
        """Test confirming a cash payment."""
        # Create payment first
        create_result = await provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        
        # Confirm it
        confirm_result = await provider.confirm_payment(payment_id)
        
        assert confirm_result["status"] == PaymentStatus.COMPLETED
        assert confirm_result["external_id"] == payment_id

    @pytest.mark.asyncio
    async def test_confirm_payment_not_found(self, provider):
        """Test confirming non-existent payment raises error."""
        with pytest.raises(ValueError, match="not found"):
            await provider.confirm_payment("unknown_payment")

    @pytest.mark.asyncio
    async def test_refund_payment_full(self, provider):
        """Test full refund of payment."""
        # Create and confirm payment
        create_result = await provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        await provider.confirm_payment(payment_id)
        
        # Refund
        refund_result = await provider.refund_payment(payment_id)
        
        assert refund_result["status"] == PaymentStatus.REFUNDED
        assert refund_result["amount"] == 1000

    @pytest.mark.asyncio
    async def test_refund_payment_partial(self, provider):
        """Test partial refund of payment."""
        # Create and confirm payment
        create_result = await provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        await provider.confirm_payment(payment_id)
        
        # Partial refund
        refund_result = await provider.refund_payment(payment_id, 500)
        
        assert refund_result["amount"] == 500

    @pytest.mark.asyncio
    async def test_refund_payment_not_found(self, provider):
        """Test refunding non-existent payment raises error."""
        with pytest.raises(ValueError, match="not found"):
            await provider.refund_payment("unknown_payment")

    @pytest.mark.asyncio
    async def test_refund_pending_payment_fails(self, provider):
        """Test refunding pending payment raises error."""
        create_result = await provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        
        with pytest.raises(ValueError, match="Cannot refund"):
            await provider.refund_payment(payment_id)

    @pytest.mark.asyncio
    async def test_get_payment_status(self, provider):
        """Test getting payment status."""
        create_result = await provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        
        status = await provider.get_payment_status(payment_id)
        assert status == PaymentStatus.PENDING
        
        await provider.confirm_payment(payment_id)
        status = await provider.get_payment_status(payment_id)
        assert status == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_payment_status_not_found(self, provider):
        """Test getting status of non-existent payment raises error."""
        with pytest.raises(ValueError, match="not found"):
            await provider.get_payment_status("unknown_payment")

    @pytest.mark.asyncio
    async def test_cancel_payment_success(self, provider):
        """Test cancelling a pending payment."""
        create_result = await provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        
        cancel_result = await provider.cancel_payment(payment_id)
        
        assert cancel_result["status"] == PaymentStatus.FAILED

    @pytest.mark.asyncio
    async def test_cancel_payment_not_found(self, provider):
        """Test cancelling non-existent payment raises error."""
        with pytest.raises(ValueError, match="not found"):
            await provider.cancel_payment("unknown_payment")

    @pytest.mark.asyncio
    async def test_cancel_completed_payment_fails(self, provider):
        """Test cancelling completed payment raises error."""
        create_result = await provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        await provider.confirm_payment(payment_id)
        
        with pytest.raises(ValueError, match="Cannot cancel"):
            await provider.cancel_payment(payment_id)
