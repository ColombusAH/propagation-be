"""
Correct unit tests for app.schemas.payment module.
"""

import pytest


@pytest.mark.unit
class TestPaymentRequestSchemas:
    """Tests for Payment request schemas."""

    def test_payment_intent_request(self):
        """Test PaymentIntentRequest schema."""
        from app.schemas.payment import PaymentIntentRequest, PaymentProviderEnum
        
        request = PaymentIntentRequest(
            order_id="ORDER123",
            amount=1000,
            currency="ILS",
            payment_provider=PaymentProviderEnum.STRIPE
        )
        assert request.order_id == "ORDER123"
        assert request.amount == 1000

    def test_payment_intent_request_default_currency(self):
        """Test PaymentIntentRequest default values."""
        from app.schemas.payment import PaymentIntentRequest
        
        request = PaymentIntentRequest(
            order_id="ORDER123",
            amount=500
        )
        assert request.currency == "ILS"

    def test_cash_payment_request(self):
        """Test CashPaymentRequest schema."""
        from app.schemas.payment import CashPaymentRequest
        
        request = CashPaymentRequest(
            order_id="ORDER456",
            amount=200,
            notes="Paid in cash"
        )
        assert request.amount == 200
        assert request.notes == "Paid in cash"

    def test_refund_request(self):
        """Test RefundRequest schema."""
        from app.schemas.payment import RefundRequest
        
        request = RefundRequest(
            payment_id="PAY789",
            reason="Defective"
        )
        assert request.payment_id == "PAY789"
        assert request.amount is None  # Optional field

    def test_payment_confirm_request(self):
        """Test PaymentConfirmRequest schema."""
        from app.schemas.payment import PaymentConfirmRequest
        
        request = PaymentConfirmRequest(
            payment_id="PAY123",
            payment_method_id="pm_card_abc"
        )
        assert request.payment_id == "PAY123"
        assert request.payment_method_id == "pm_card_abc"


@pytest.mark.unit
class TestPaymentResponseSchemas:
    """Tests for Payment response schemas."""

    def test_payment_intent_response(self):
        """Test PaymentIntentResponse schema."""
        from app.schemas.payment import PaymentIntentResponse, PaymentStatusEnum, PaymentProviderEnum
        
        response = PaymentIntentResponse(
            payment_id="internal_123",
            external_id="ext_456",
            amount=1000,
            currency="ILS",
            status=PaymentStatusEnum.PENDING,
            provider=PaymentProviderEnum.STRIPE
        )
        assert response.payment_id == "internal_123"
        assert response.status == PaymentStatusEnum.PENDING

    def test_refund_response(self):
        """Test RefundResponse schema."""
        from app.schemas.payment import RefundResponse, PaymentStatusEnum
        
        response = RefundResponse(
            payment_id="PAY123",
            refund_id="REF456",
            amount=500,
            status=PaymentStatusEnum.REFUNDED
        )
        assert response.amount == 500
        assert response.status == PaymentStatusEnum.REFUNDED

    def test_payment_status_response(self):
        """Test PaymentStatusResponse schema."""
        from app.schemas.payment import PaymentStatusResponse, PaymentStatusEnum, PaymentProviderEnum
        from datetime import datetime
        
        now = datetime.now()
        response = PaymentStatusResponse(
            payment_id="PAY123",
            status=PaymentStatusEnum.COMPLETED,
            amount=1000,
            currency="ILS",
            provider=PaymentProviderEnum.CASH,
            created_at=now
        )
        assert response.created_at == now
        assert response.provider == PaymentProviderEnum.CASH


@pytest.mark.unit
class TestPaymentEnums:
    """Tests for Payment enums."""

    def test_provider_enum_values(self):
        """Test PaymentProviderEnum values."""
        from app.schemas.payment import PaymentProviderEnum
        
        assert PaymentProviderEnum.STRIPE == "STRIPE"
        assert PaymentProviderEnum.TRANZILA == "TRANZILA"
        assert PaymentProviderEnum.CASH == "CASH"

    def test_status_enum_values(self):
        """Test PaymentStatusEnum values."""
        from app.schemas.payment import PaymentStatusEnum
        
        assert PaymentStatusEnum.PENDING == "PENDING"
        assert PaymentStatusEnum.COMPLETED == "COMPLETED"
        assert PaymentStatusEnum.FAILED == "FAILED"
