"""
Payment schemas for API requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PaymentProviderEnum(str, Enum):
    """Payment provider options."""

    STRIPE = "STRIPE"
    TRANZILA = "TRANZILA"
    NEXI = "NEXI"
    CASH = "CASH"


class PaymentStatusEnum(str, Enum):
    """Payment status options."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentIntentRequest(BaseModel):
    """Request to create a payment intent."""

    order_id: str = Field(..., description="Order ID")
    amount: int = Field(..., description="Amount in agorot/cents", gt=0)
    currency: str = Field(default="ILS", description="Currency code")
    payment_provider: PaymentProviderEnum = Field(
        default=PaymentProviderEnum.STRIPE, description="Payment provider to use"
    )
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


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
