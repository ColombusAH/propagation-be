"""Base payment gateway interface and shared types."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    TRANZILA = "tranzila"
    CASH = "cash"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentRequest(BaseModel):
    """Request to create a new payment."""

    order_id: str
    amount: int  # in cents/agorot
    currency: str = "ILS"
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    return_url: Optional[str] = None
    metadata: Optional[dict] = None


class PaymentResult(BaseModel):
    """Result from a payment operation."""

    success: bool
    payment_id: str
    external_id: Optional[str] = None
    redirect_url: Optional[str] = None  # For 3DS/redirect flows
    client_secret: Optional[str] = None  # For Stripe Elements
    error: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING


class RefundResult(BaseModel):
    """Result from a refund operation."""

    success: bool
    refund_id: Optional[str] = None
    error: Optional[str] = None


class PaymentGateway(ABC):
    """Abstract base class for payment gateways."""

    @property
    @abstractmethod
    def provider(self) -> PaymentProvider:
        """Return the provider type."""
        pass

    @abstractmethod
    async def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a new payment intent/session."""
        pass

    @abstractmethod
    async def confirm_payment(
        self, payment_id: str, payment_method: Optional[str] = None
    ) -> PaymentResult:
        """Confirm a pending payment."""
        pass

    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """Get the status of a payment."""
        pass

    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> RefundResult:
        """Refund a payment (full or partial)."""
        pass
