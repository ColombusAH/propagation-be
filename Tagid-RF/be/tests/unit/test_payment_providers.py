"""
Unit tests for payment provider base class and implementations.
"""

import pytest

from app.services.cash_provider import CashProvider
from app.services.payment_provider import PaymentProvider


@pytest.mark.unit
def test_payment_provider_is_abstract():
    """Test that PaymentProvider cannot be instantiated directly."""
    with pytest.raises(TypeError):
        PaymentProvider()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cash_provider_initialization():
    """Test CashProvider initialization."""
    provider = CashProvider()
    assert provider is not None
    assert isinstance(provider.pending_payments, dict)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cash_provider_create_payment():
    """Test creating a cash payment."""
    provider = CashProvider()

    result = await provider.create_payment_intent(
        amount=10000, currency="ILS", metadata={"user_id": "test-123"}  # 100 ILS
    )

    assert result is not None
    assert "payment_id" in result
    assert result["status"].value == "PENDING"
