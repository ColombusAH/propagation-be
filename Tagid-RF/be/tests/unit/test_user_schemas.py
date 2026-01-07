"""
Unit tests for User and Payment schemas.
Using actual schema names from the codebase.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime


@pytest.mark.unit
class TestUserSchemas:
    """Tests for User Pydantic schemas."""

    def test_user_register_schema(self):
        """Test UserRegister schema with valid data."""
        from app.schemas.user import UserRegister
        
        user = UserRegister(
            email="test@example.com",
            password="securepassword123",
            name="Test User",
            phone="+972501234567",
            address="123 Main St",
            businessId="123456789"
        )
        
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == "CUSTOMER"  # Default

    def test_user_register_requires_email(self):
        """Test UserRegister requires email."""
        from app.schemas.user import UserRegister
        
        with pytest.raises(ValidationError):
            UserRegister(
                password="password123",
                name="Test",
                phone="123",
                address="addr",
                businessId="123"
            )

    def test_user_register_requires_password(self):
        """Test UserRegister requires password."""
        from app.schemas.user import UserRegister
        
        with pytest.raises(ValidationError):
            UserRegister(
                email="test@example.com",
                name="Test",
                phone="123",
                address="addr",
                businessId="123"
            )

    def test_user_register_password_min_length(self):
        """Test UserRegister password minimum length."""
        from app.schemas.user import UserRegister
        
        with pytest.raises(ValidationError):
            UserRegister(
                email="test@example.com",
                password="short",  # Too short
                name="Test",
                phone="123",
                address="addr",
                businessId="123"
            )

    def test_user_login_schema(self):
        """Test UserLogin schema."""
        from app.schemas.user import UserLogin
        
        login = UserLogin(
            email="user@example.com",
            password="password123"
        )
        
        assert login.email == "user@example.com"
        assert login.password == "password123"

    def test_user_response_schema(self):
        """Test UserResponse schema."""
        from app.schemas.user import UserResponse
        
        now = datetime.now()
        user = UserResponse(
            id="user123",
            email="test@example.com",
            name="Test User",
            phone="+972501234567",
            address="123 Main St",
            role="CUSTOMER",
            businessId="123456789",
            createdAt=now
        )
        
        assert user.id == "user123"
        assert user.role == "CUSTOMER"

    def test_token_response_schema(self):
        """Test TokenResponse schema."""
        from app.schemas.user import TokenResponse
        
        token = TokenResponse(
            message="Login successful",
            user_id="user123",
            role="CUSTOMER",
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        )
        
        assert token.message == "Login successful"
        assert token.user_id == "user123"


@pytest.mark.unit
class TestPaymentSchemas:
    """Tests for Payment Pydantic schemas."""

    def test_payment_provider_enum(self):
        """Test PaymentProviderEnum values."""
        from app.schemas.payment import PaymentProviderEnum
        
        assert PaymentProviderEnum.STRIPE.value == "STRIPE"
        assert PaymentProviderEnum.TRANZILA.value == "TRANZILA"
        assert PaymentProviderEnum.CASH.value == "CASH"

    def test_payment_status_enum(self):
        """Test PaymentStatusEnum values."""
        from app.schemas.payment import PaymentStatusEnum
        
        assert PaymentStatusEnum.PENDING.value == "PENDING"
        assert PaymentStatusEnum.COMPLETED.value == "COMPLETED"
        assert PaymentStatusEnum.REFUNDED.value == "REFUNDED"

    def test_payment_intent_request(self):
        """Test PaymentIntentRequest schema."""
        from app.schemas.payment import PaymentIntentRequest
        
        intent = PaymentIntentRequest(
            order_id="order123",
            amount=15000,
            currency="ILS"
        )
        
        assert intent.order_id == "order123"
        assert intent.amount == 15000
        assert intent.currency == "ILS"

    def test_payment_intent_response(self):
        """Test PaymentIntentResponse schema."""
        from app.schemas.payment import PaymentIntentResponse, PaymentStatusEnum, PaymentProviderEnum
        
        response = PaymentIntentResponse(
            payment_id="pay123",
            external_id="ext123",
            amount=15000,
            currency="ILS",
            status=PaymentStatusEnum.PENDING,
            provider=PaymentProviderEnum.STRIPE
        )
        
        assert response.payment_id == "pay123"
        assert response.status == PaymentStatusEnum.PENDING

    def test_cash_payment_request(self):
        """Test CashPaymentRequest schema."""
        from app.schemas.payment import CashPaymentRequest
        
        cash = CashPaymentRequest(
            order_id="order123",
            amount=5000,
            notes="Cash payment"
        )
        
        assert cash.order_id == "order123"
        assert cash.amount == 5000

    def test_refund_request(self):
        """Test RefundRequest schema."""
        from app.schemas.payment import RefundRequest
        
        refund = RefundRequest(
            payment_id="pay123",
            amount=5000,
            reason="Customer request"
        )
        
        assert refund.payment_id == "pay123"
        assert refund.reason == "Customer request"


@pytest.mark.unit
class TestEmailValidation:
    """Tests for email validation."""

    def test_valid_emails(self):
        """Test valid email formats."""
        from app.schemas.user import UserLogin
        
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user@subdomain.example.com"
        ]
        
        for email in valid_emails:
            login = UserLogin(email=email, password="password123")
            assert login.email == email

    def test_invalid_email_rejected(self):
        """Test invalid email format is rejected."""
        from app.schemas.user import UserLogin
        
        with pytest.raises(ValidationError):
            UserLogin(email="not-an-email", password="password123")
