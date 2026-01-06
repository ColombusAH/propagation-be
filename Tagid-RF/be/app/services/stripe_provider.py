"""
Stripe payment provider implementation.
Handles credit/debit card payments via Stripe API.
"""

import logging
from typing import Any, Dict, Optional

import stripe

from app.core.config import settings
from app.services.payment_provider import PaymentProvider, PaymentStatus

logger = logging.getLogger(__name__)


class StripeProvider(PaymentProvider):
    """
    Stripe payment provider for credit/debit card transactions.
    """

    def __init__(self):
        """Initialize Stripe provider with API keys."""
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        logger.info("Stripe provider initialized")

    async def create_payment_intent(
        self, amount: int, currency: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe payment intent.

        Args:
            amount: Amount in agorot/cents
            currency: Currency code (e.g., "ILS", "USD")
            metadata: Additional metadata

        Returns:
            Payment intent details including client_secret
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True},
            )

            logger.info(f"Created Stripe payment intent: {intent.id} for {amount} {currency}")

            return {
                "payment_id": intent.id,
                "external_id": intent.id,
                "client_secret": intent.client_secret,
                "status": PaymentStatus.PENDING,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            raise ValueError(f"Failed to create payment intent: {str(e)}")

    async def confirm_payment(
        self, payment_id: str, payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirm a Stripe payment intent.

        Args:
            payment_id: Stripe payment intent ID
            payment_method_id: Stripe payment method ID

        Returns:
            Confirmation details
        """
        try:
            if payment_method_id:
                intent = stripe.PaymentIntent.confirm(payment_id, payment_method=payment_method_id)
            else:
                intent = stripe.PaymentIntent.retrieve(payment_id)

            status = self._map_stripe_status(intent.status)

            logger.info(f"Stripe payment {payment_id} status: {status}")

            return {
                "status": status,
                "external_id": intent.id,
                "metadata": {
                    "stripe_status": intent.status,
                    "payment_method": intent.payment_method,
                },
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment: {str(e)}")
            raise ValueError(f"Failed to confirm payment: {str(e)}")

    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Refund a Stripe payment.

        Args:
            payment_id: Stripe payment intent ID
            amount: Amount to refund (None for full refund)

        Returns:
            Refund details
        """
        try:
            refund_params = {"payment_intent": payment_id}
            if amount:
                refund_params["amount"] = amount

            refund = stripe.Refund.create(**refund_params)

            logger.info(f"Stripe refund created: {refund.id} for payment {payment_id}")

            return {
                "status": PaymentStatus.REFUNDED,
                "refund_id": refund.id,
                "amount": refund.amount,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating refund: {str(e)}")
            raise ValueError(f"Failed to create refund: {str(e)}")

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """
        Get the current status of a Stripe payment.

        Args:
            payment_id: Stripe payment intent ID

        Returns:
            Payment status
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_id)
            return self._map_stripe_status(intent.status)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment: {str(e)}")
            raise ValueError(f"Failed to retrieve payment: {str(e)}")

    async def cancel_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Cancel a Stripe payment intent.

        Args:
            payment_id: Stripe payment intent ID

        Returns:
            Cancellation details
        """
        try:
            intent = stripe.PaymentIntent.cancel(payment_id)

            logger.info(f"Stripe payment cancelled: {payment_id}")

            return {
                "status": PaymentStatus.FAILED,
                "message": "Payment cancelled",
                "external_id": intent.id,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling payment: {str(e)}")
            raise ValueError(f"Failed to cancel payment: {str(e)}")

    def _map_stripe_status(self, stripe_status: str) -> PaymentStatus:
        """Map Stripe status to internal PaymentStatus."""
        status_map = {
            "requires_payment_method": PaymentStatus.PENDING,
            "requires_confirmation": PaymentStatus.PENDING,
            "requires_action": PaymentStatus.PROCESSING,
            "processing": PaymentStatus.PROCESSING,
            "succeeded": PaymentStatus.COMPLETED,
            "canceled": PaymentStatus.FAILED,
        }
        return status_map.get(stripe_status, PaymentStatus.FAILED)
