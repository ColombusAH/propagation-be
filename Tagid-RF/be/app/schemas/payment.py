"""
Payment schemas for API requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PaymentProviderEnum(str, Enum):
    """
    Supported payment providers.

    - STRIPE: International credit card processing
    - TRANZILA: Israeli payment gateway
    - NEXI: European payment processor
    - CASH: Cash payments (recorded manually)
    """

    STRIPE = "STRIPE"
    TRANZILA = "TRANZILA"
    NEXI = "NEXI"
    CASH = "CASH"


class PaymentStatusEnum(str, Enum):
    """
    Payment processing status.

    - PENDING: Payment created but not yet processed
    - PROCESSING: Payment is being processed by provider
    - COMPLETED: Payment successfully completed
    - FAILED: Payment failed (card declined, insufficient funds, etc.)
    - REFUNDED: Payment was refunded to customer
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentIntentRequest(BaseModel):
    """
    Request to create a payment intent.

    A payment intent represents the intention to collect payment.
    Create this before showing payment UI to the customer.

    Example:
        ```python
        intent = PaymentIntentRequest(
            order_id="order_123",
            amount=15000,  # 150.00 ILS in agorot
            currency="ILS",
            payment_provider="STRIPE"
        )
        ```
    """

    order_id: str = Field(..., description="Order ID to associate with this payment")
    amount: int = Field(
        ...,
        description="Amount in smallest currency unit (agorot for ILS, cents for USD)",
        gt=0,
        examples=[15000, 5000, 100000],
    )
    currency: str = Field(
        default="ILS",
        description="ISO 4217 currency code (ILS, USD, EUR, etc.)",
        examples=["ILS", "USD", "EUR"],
    )
    payment_provider: PaymentProviderEnum = Field(
        default=PaymentProviderEnum.STRIPE,
        description="Payment provider to use for processing",
    )
    metadata: Optional[dict] = Field(
        default=None, description="Additional metadata to store with payment"
    )


class PaymentIntentResponse(BaseModel):
    """Response from creating a payment intent."""

    payment_id: str = Field(..., description="Internal payment ID")
    external_id: str = Field(..., description="Provider's payment ID")
    client_secret: Optional[str] = Field(None, description="Client secret for Stripe")
    amount: int = Field(..., description="Amount in agorot/cents")
    currency: str = Field(..., description="Currency code")
    status: PaymentStatusEnum = Field(..., description="Payment status")
    provider: PaymentProviderEnum = Field(..., description="Payment provider")


class PaymentConfirmRequest(BaseModel):
    """Request to confirm a payment."""

    payment_id: str = Field(..., description="Payment ID")
    payment_method_id: Optional[str] = Field(None, description="Payment method ID (for Stripe)")


class PaymentConfirmResponse(BaseModel):
    """Response from confirming a payment."""

    payment_id: str = Field(..., description="Payment ID")
    status: PaymentStatusEnum = Field(..., description="Payment status")
    external_id: str = Field(..., description="Provider's payment ID")
    metadata: Optional[dict] = Field(default=None, description="Additional data")


class CashPaymentRequest(BaseModel):
    """Request to record a cash payment."""

    order_id: str = Field(..., description="Order ID")
    amount: int = Field(..., description="Amount in agorot", gt=0)
    notes: Optional[str] = Field(None, description="Payment notes")


class RefundRequest(BaseModel):
    """Request to refund a payment."""

    payment_id: str = Field(..., description="Payment ID")
    amount: Optional[int] = Field(
        None, description="Amount to refund in agorot (None for full refund)"
    )
    reason: Optional[str] = Field(None, description="Refund reason")


class RefundResponse(BaseModel):
    """Response from refunding a payment."""

    payment_id: str = Field(..., description="Payment ID")
    refund_id: str = Field(..., description="Refund ID")
    amount: int = Field(..., description="Refunded amount in agorot")
    status: PaymentStatusEnum = Field(..., description="Payment status")


class PaymentStatusResponse(BaseModel):
    """Response for payment status query."""

    payment_id: str = Field(..., description="Payment ID")
    status: PaymentStatusEnum = Field(..., description="Payment status")
    amount: int = Field(..., description="Amount in agorot")
    currency: str = Field(..., description="Currency code")
    provider: PaymentProviderEnum = Field(..., description="Payment provider")
    created_at: datetime = Field(..., description="Creation timestamp")
    paid_at: Optional[datetime] = Field(None, description="Payment completion timestamp")
