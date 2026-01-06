"""
Abstract base class for payment providers.
Defines the interface that all payment providers must implement.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional


class PaymentStatus(str, Enum):
    """Payment status enum matching Prisma schema."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers.
    All payment providers (Stripe, Tranzila, Nexi, Cash) must implement these methods.
    """

    @abstractmethod
    async def create_payment_intent(
        self,
        amount: int,  # in agorot/cents
        currency: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment intent/transaction.

        Args:
            amount: Amount in smallest currency unit (agorot for ILS, cents for USD)
            currency: Currency code (e.g., "ILS", "USD")
            metadata: Additional metadata for the payment

        Returns:
            Dict containing:
                - payment_id: Internal payment ID
                - external_id: Provider's transaction ID
                - client_secret: Secret for client-side confirmation (if applicable)
                - status: Payment status
        """
        pass

    @abstractmethod
    async def confirm_payment(
        self, payment_id: str, payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirm a payment.

        Args:
            payment_id: Internal payment ID
            payment_method_id: Provider-specific payment method ID (e.g., Stripe payment method)

        Returns:
            Dict containing:
                - status: Payment status
                - external_id: Provider's transaction ID
                - metadata: Additional provider data
        """
        pass

    @abstractmethod
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Refund a payment (full or partial).

        Args:
            payment_id: Internal payment ID
            amount: Amount to refund (None for full refund)

        Returns:
            Dict containing:
                - status: Refund status
                - refund_id: Provider's refund ID
        """
        pass

    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """
        Get the current status of a payment.

        Args:
            payment_id: Internal payment ID

        Returns:
            PaymentStatus enum value
        """
        pass

    @abstractmethod
    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Cancel a pending payment.

        Args:
            payment_id: Internal payment ID

        Returns:
            Dict containing cancellation status
        """
        pass
