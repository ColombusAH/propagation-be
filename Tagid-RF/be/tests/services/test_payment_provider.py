"""
Tests for Payment Gateway Services - Factory and base classes.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.payment_provider import PaymentProvider, PaymentStatus


class TestPaymentStatus:
    """Test PaymentStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert PaymentStatus.PENDING is not None
        assert PaymentStatus.COMPLETED is not None
        assert PaymentStatus.FAILED is not None
        assert PaymentStatus.REFUNDED is not None
        assert PaymentStatus.PROCESSING is not None


class TestPaymentProvider:
    """Test PaymentProvider base class."""

    def test_is_abstract(self):
        """PaymentProvider should be abstract."""
        # Can't instantiate directly
        with pytest.raises(TypeError):
            PaymentProvider()

    def test_has_required_methods(self):
        """Check required abstract methods exist."""
        assert hasattr(PaymentProvider, "create_payment_intent")
        assert hasattr(PaymentProvider, "confirm_payment")
        assert hasattr(PaymentProvider, "refund_payment")
        assert hasattr(PaymentProvider, "get_payment_status")
        assert hasattr(PaymentProvider, "cancel_payment")
