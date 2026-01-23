"""
Nexi payment provider implementation.
Handles Israeli payment terminal (מסופון נייקס) transactions.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from app.core.config import settings
from app.services.payment_provider import PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class NexiProvider(PaymentProvider):
    """
    Nexi payment provider for Israeli payment terminals.
    """

    def __init__(self):
        """Initialize Nexi provider with credentials."""
        self.terminal_id = settings.NEXI_TERMINAL_ID
        self.api_key = settings.NEXI_API_KEY
        self.api_endpoint = settings.NEXI_API_ENDPOINT
        self.merchant_id = settings.NEXI_MERCHANT_ID
        self.pending_transactions: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Nexi provider initialized for terminal: {self.terminal_id}")

    async def create_payment_intent(
        self, amount: int, currency: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Nexi payment transaction.

        Args:
            amount: Amount in agorot
            currency: Currency code (should be "ILS")
            metadata: Additional metadata

        Returns:
            Payment transaction details
        """
        try:
            # Convert agorot to shekels for Nexi
            amount_ils = amount / 100

            transaction_id = f"nexi_{datetime.now().timestamp()}"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_endpoint}/payments",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "merchant_id": self.merchant_id,
                        "terminal_id": self.terminal_id,
                        "amount": amount_ils,
                        "currency": currency,
                        "transaction_id": transaction_id,
                        "metadata": metadata or {},
                    },
                    timeout=30.0,
                )

            if response.status_code in [200, 201]:
                result = response.json()

                # Store transaction
                self.pending_transactions[transaction_id] = {
                    "amount": amount,
                    "currency": currency,
                    "status": PaymentStatus.PENDING,
                    "created_at": datetime.now().isoformat(),
                    "metadata": metadata or {},
                    "nexi_response": result,
                }

                logger.info(
                    f"Created Nexi transaction: {transaction_id} for {amount_ils} ILS"
                )

                return {
                    "payment_id": transaction_id,
                    "external_id": result.get("transaction_id", transaction_id),
                    "client_secret": None,
                    "status": PaymentStatus.PENDING,
                }
            else:
                raise ValueError(
                    f"Nexi API error: {response.status_code} - {response.text}"
                )

        except Exception as e:
            logger.error(f"Nexi error creating transaction: {str(e)}")
            raise ValueError(f"Failed to create Nexi transaction: {str(e)}")

    async def confirm_payment(
        self, payment_id: str, payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirm a Nexi payment.

        Args:
            payment_id: Transaction ID
            payment_method_id: Not used for Nexi

        Returns:
            Confirmation details
        """
        if payment_id not in self.pending_transactions:
            raise ValueError(f"Transaction {payment_id} not found")

        transaction = self.pending_transactions[payment_id]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_endpoint}/payments/{payment_id}/confirm",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )

            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "completed")

                transaction["status"] = (
                    PaymentStatus.COMPLETED
                    if status == "completed"
                    else PaymentStatus.PROCESSING
                )
                transaction["confirmed_at"] = datetime.now().isoformat()

                logger.info(f"Nexi payment confirmed: {payment_id}")

                return {
                    "status": transaction["status"],
                    "external_id": payment_id,
                    "metadata": result,
                }
            else:
                raise ValueError(f"Nexi confirmation failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Nexi error confirming payment: {str(e)}")
            raise ValueError(f"Failed to confirm payment: {str(e)}")

    async def refund_payment(
        self, payment_id: str, amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Refund a Nexi payment.

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
                    f"{self.api_endpoint}/payments/{payment_id}/refund",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"amount": refund_amount_ils},
                    timeout=30.0,
                )

            if response.status_code == 200:
                result = response.json()
                transaction["status"] = PaymentStatus.REFUNDED
                transaction["refunded_at"] = datetime.now().isoformat()

                logger.info(f"Nexi refund created for {payment_id}")

                return {
                    "status": PaymentStatus.REFUNDED,
                    "refund_id": result.get("refund_id", f"{payment_id}_refund"),
                    "amount": refund_amount,
                }
            else:
                raise ValueError(f"Nexi refund failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Nexi error creating refund: {str(e)}")
            raise ValueError(f"Failed to create refund: {str(e)}")

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """
        Get the current status of a Nexi payment.

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
        Cancel a Nexi payment.

        Args:
            payment_id: Transaction ID

        Returns:
            Cancellation details
        """
        if payment_id not in self.pending_transactions:
            raise ValueError(f"Transaction {payment_id} not found")

        transaction = self.pending_transactions[payment_id]

        if transaction["status"] != PaymentStatus.PENDING:
            raise ValueError(
                f"Cannot cancel transaction with status {transaction['status']}"
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_endpoint}/payments/{payment_id}/cancel",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )

            if response.status_code == 200:
                transaction["status"] = PaymentStatus.FAILED
                transaction["cancelled_at"] = datetime.now().isoformat()

                logger.info(f"Nexi payment cancelled: {payment_id}")

                return {"status": PaymentStatus.FAILED, "message": "Payment cancelled"}
            else:
                raise ValueError(f"Nexi cancellation failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Nexi error cancelling payment: {str(e)}")
            raise ValueError(f"Failed to cancel payment: {str(e)}")
