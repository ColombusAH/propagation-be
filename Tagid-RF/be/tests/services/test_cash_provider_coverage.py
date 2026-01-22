"""
Coverage tests for Cash Provider.
"""
import pytest
from app.services.cash_provider import CashProvider
from app.services.payment_provider import PaymentStatus

class TestCashProviderCoverage:

    def setup_method(self):
        self.provider = CashProvider()
        # Pre-seed a transaction
        self.provider.pending_payments["tx1"] = {
            "amount": 1000,
            "currency": "ILS",
            "status": PaymentStatus.PENDING,
            "created_at": "2023-01-01T00:00:00"
        }
        self.provider.pending_payments["tx_completed"] = {
            "amount": 1000,
            "currency": "ILS",
            "status": PaymentStatus.COMPLETED,
            "created_at": "2023-01-01T00:00:00"
        }

    async def test_confirm_payment_not_found(self):
        """Test confirm payment for unknown ID."""
        with pytest.raises(ValueError) as exc:
            await self.provider.confirm_payment("unknown")
        assert "not found" in str(exc.value)

    async def test_refund_payment_not_found(self):
        """Test refund for unknown ID."""
        with pytest.raises(ValueError) as exc:
            await self.provider.refund_payment("unknown")
        assert "not found" in str(exc.value)

    async def test_refund_payment_invalid_status(self):
        """Test refund for non-completed payment."""
        with pytest.raises(ValueError) as exc:
            await self.provider.refund_payment("tx1")  # tx1 is PENDING
        assert "Cannot refund" in str(exc.value)

    async def test_get_payment_status_not_found(self):
        """Test get status for unknown ID."""
        with pytest.raises(ValueError) as exc:
            await self.provider.get_payment_status("unknown")
        assert "not found" in str(exc.value)

    async def test_cancel_payment_not_found(self):
        """Test cancel for unknown ID."""
        with pytest.raises(ValueError) as exc:
            await self.provider.cancel_payment("unknown")
        assert "not found" in str(exc.value)

    async def test_cancel_payment_invalid_status(self):
        """Test cancel for non-pending payment."""
        with pytest.raises(ValueError) as exc:
            await self.provider.cancel_payment("tx_completed")
        assert "Cannot cancel" in str(exc.value)
