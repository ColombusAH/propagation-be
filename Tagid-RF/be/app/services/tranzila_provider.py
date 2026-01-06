"""
Tranzila payment provider implementation.
Handles Israeli payment terminal (מסופון טרנזילה) transactions.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.services.payment_provider import PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class TranzilaProvider(PaymentProvider):
    """
    Tranzila payment provider for Israeli payment terminals.
    """

    def __init__(self):
        """Initialize Tranzila provider with credentials."""
        self.terminal_name = settings.TRANZILA_TERMINAL_NAME
        self.api_key = settings.TRANZILA_API_KEY
        self.api_endpoint = settings.TRANZILA_API_ENDPOINT
        self.pending_transactions: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Tranzila provider initialized for terminal: {self.terminal_name}")

    async def create_payment_intent(
        self, amount: int, currency: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Tranzila payment transaction.

        Args:
            amount: Amount in agorot
            currency: Currency code (should be "ILS")
            metadata: Additional metadata

        Returns:
            Payment transaction details
        """
        try:
            # Convert agorot to shekels for Tranzila
            amount_ils = amount / 100

            transaction_id = f"trz_{datetime.now().timestamp()}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_endpoint,
                    data={
                        "supplier": self.terminal_name,
                        "sum": amount_ils,
                        "currency": "1",  # ILS
                        "tranmode": "VK",  # Credit card
                        "TranzilaPW": self.api_key,
                        "cred_type": "1",  # Regular credit
                        "order_id": transaction_id,
                    },
                    timeout=30.0,
                )

            if response.status_code == 200:
                result = response.text

                # Store transaction
                self.pending_transactions[transaction_id] = {
                    "amount": amount,
                    "currency": currency,
                    "status": PaymentStatus.PENDING,
                    "created_at": datetime.now().isoformat(),
                    "metadata": metadata or {},
                    "tranzila_response": result,
                }

                logger.info(f"Created Tranzila transaction: {transaction_id} for {amount_ils} ILS")

                return {
                    "payment_id": transaction_id,
                    "external_id": transaction_id,
                    "client_secret": None,  # Tranzila handles this differently
                    "status": PaymentStatus.PENDING,
                }
            else:
                raise ValueError(f"Tranzila API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Tranzila error creating transaction: {str(e)}")
            raise ValueError(f"Failed to create Tranzila transaction: {str(e)}")

    async def confirm_payment(
        self, payment_id: str, payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirm a Tranzila payment.

        Args:
            payment_id: Transaction ID
            payment_method_id: Not used for Tranzila

        Returns:
            Confirmation details
        """
        if payment_id not in self.pending_transactions:
            raise ValueError(f"Transaction {payment_id} not found")

        transaction = self.pending_transactions[payment_id]

        # In real implementation, check Tranzila callback/webhook
        # For now, mark as completed
        transaction["status"] = PaymentStatus.COMPLETED
        transaction["confirmed_at"] = datetime.now().isoformat()

        logger.info(f"Tranzila payment confirmed: {payment_id}")

        return {
            "status": PaymentStatus.COMPLETED,
            "external_id": payment_id,
            "metadata": transaction.get("metadata", {}),
        }

    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Refund a Tranzila payment.

        Args:
            payment_id: Transaction ID
            amount: Amount to refund (None for full refund)

        Returns:
            Refund details
        """
        if payment_id not in self.pending_transactions:
            raise ValueError(f"Transaction {payment_id} not found")

        transaction = self.pending_transactions[payment_id]
        refund_amount = amount or transaction["amount"]
        refund_amount_ils = refund_amount / 100

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_endpoint,
                    data={
                        "supplier": self.terminal_name,
                        "sum": refund_amount_ils,
                        "currency": "1",
                        "tranmode": "C",  # Credit/Refund
                        "TranzilaPW": self.api_key,
                        "order_id": payment_id,
                    },
                    timeout=30.0,
                )

            if response.status_code == 200:
                transaction["status"] = PaymentStatus.REFUNDED
                transaction["refunded_at"] = datetime.now().isoformat()

                logger.info(f"Tranzila refund created for {payment_id}")

                return {
                    "status": PaymentStatus.REFUNDED,
                    "refund_id": f"{payment_id}_refund",
                    "amount": refund_amount,
                }
            else:
                raise ValueError(f"Tranzila refund failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Tranzila error creating refund: {str(e)}")
            raise ValueError(f"Failed to create refund: {str(e)}")

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """
        Get the current status of a Tranzila payment.

        Args:
            payment_id: Transaction ID

        Returns:
            Payment status
        """
        if payment_id not in self.pending_transactions:
            raise ValueError(f"Transaction {payment_id} not found")

        return self.pending_transactions[payment_id]["status"]

    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Cancel a Tranzila payment.

        Args:
            payment_id: Transaction ID

        Returns:
            Cancellation details
        """
        if payment_id not in self.pending_transactions:
            raise ValueError(f"Transaction {payment_id} not found")

        transaction = self.pending_transactions[payment_id]

        if transaction["status"] != PaymentStatus.PENDING:
            raise ValueError(f"Cannot cancel transaction with status {transaction['status']}")

        transaction["status"] = PaymentStatus.FAILED
        transaction["cancelled_at"] = datetime.now().isoformat()

        logger.info(f"Tranzila payment cancelled: {payment_id}")

        return {"status": PaymentStatus.FAILED, "message": "Payment cancelled"}
