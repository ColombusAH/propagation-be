"""
Cash payment provider implementation.
Handles in-store cash payments that require manual confirmation by store managers.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from app.services.payment_provider import PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class CashProvider(PaymentProvider):
    """
    Cash payment provider for in-store cash transactions.
    Payments are marked as PENDING until confirmed by a store manager.
    """

    def __init__(self):
        """Initialize cash provider."""
        self.pending_payments: Dict[str, Dict[str, Any]] = {}

    async def create_payment_intent(
        self, amount: int, currency: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a cash payment intent.
        Cash payments start as PENDING and require manual confirmation.

        Args:
            amount: Amount in agorot
            currency: Currency code (should be "ILS")
            metadata: Additional metadata

        Returns:
            Payment intent details
        """
        payment_id = f"cash_{datetime.now().timestamp()}"

        payment_data = {
            "amount": amount,
            "currency": currency,
            "status": PaymentStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self.pending_payments[payment_id] = payment_data

        logger.info(
            f"Created cash payment intent: {payment_id} for {amount} {currency}"
        )

        return {
            "payment_id": payment_id,
            "external_id": payment_id,  # Same as internal ID for cash
            "client_secret": None,  # No client secret needed for cash
            "status": PaymentStatus.PENDING,
        }

    async def confirm_payment(
        self, payment_id: str, payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirm a cash payment (called by store manager).

        Args:
            payment_id: Internal payment ID
            payment_method_id: Not used for cash payments

        Returns:
            Confirmation details
        """
        if payment_id not in self.pending_payments:
            raise ValueError(f"Payment {payment_id} not found")

        payment = self.pending_payments[payment_id]
        payment["status"] = PaymentStatus.COMPLETED
        payment["confirmed_at"] = datetime.now().isoformat()

        logger.info(f"Cash payment confirmed: {payment_id}")

        return {
            "status": PaymentStatus.COMPLETED,
            "external_id": payment_id,
            "metadata": payment.get("metadata", {}),
        }

    async def refund_payment(
        self, payment_id: str, amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Refund a cash payment.

        Args:
            payment_id: Internal payment ID
            amount: Amount to refund (None for full refund)

        Returns:
            Refund details
        """
        if payment_id not in self.pending_payments:
            raise ValueError(f"Payment {payment_id} not found")

        payment = self.pending_payments[payment_id]

        if payment["status"] != PaymentStatus.COMPLETED:
            raise ValueError(f"Cannot refund payment with status {payment['status']}")

        refund_amount = amount or payment["amount"]
        payment["status"] = PaymentStatus.REFUNDED
        payment["refunded_at"] = datetime.now().isoformat()
        payment["refund_amount"] = refund_amount

        logger.info(f"Cash payment refunded: {payment_id}, amount: {refund_amount}")

        return {
            "status": PaymentStatus.REFUNDED,
            "refund_id": f"{payment_id}_refund",
            "amount": refund_amount,
        }

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """
        Get the current status of a cash payment.

        Args:
            payment_id: Internal payment ID

        Returns:
            Payment status
        """
        if payment_id not in self.pending_payments:
            raise ValueError(f"Payment {payment_id} not found")

        return self.pending_payments[payment_id]["status"]

    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Cancel a pending cash payment.

        Args:
            payment_id: Internal payment ID

        Returns:
            Cancellation details
        """
        if payment_id not in self.pending_payments:
            raise ValueError(f"Payment {payment_id} not found")

        payment = self.pending_payments[payment_id]

        if payment["status"] != PaymentStatus.PENDING:
            raise ValueError(f"Cannot cancel payment with status {payment['status']}")

        payment["status"] = PaymentStatus.FAILED
        payment["cancelled_at"] = datetime.now().isoformat()

        logger.info(f"Cash payment cancelled: {payment_id}")

        return {"status": PaymentStatus.FAILED, "message": "Payment cancelled"}
