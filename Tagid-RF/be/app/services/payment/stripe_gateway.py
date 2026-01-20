"""Stripe payment gateway integration."""

import logging
from typing import Optional

from .base import (
    PaymentGateway,
    PaymentProvider,
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
    RefundResult,
)

logger = logging.getLogger(__name__)

# Try to import stripe, but don't fail if not installed
try:
    import stripe

    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("Stripe library not installed. Run: pip install stripe")


class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation."""

    def __init__(self, api_key: str, webhook_secret: Optional[str] = None):
        if not STRIPE_AVAILABLE:
            raise RuntimeError("Stripe library is not installed")

        self.api_key = api_key
        self.webhook_secret = webhook_secret
        stripe.api_key = api_key

    @property
    def provider(self) -> PaymentProvider:
        return PaymentProvider.STRIPE

    async def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a Stripe Payment Intent."""
        try:
            intent = stripe.PaymentIntent.create(
                amount=request.amount,
                currency=request.currency.lower(),
                metadata={"order_id": request.order_id, **(request.metadata or {})},
                receipt_email=request.customer_email,
                automatic_payment_methods={"enabled": True},
            )

            logger.info(f"Created Stripe payment intent: {intent.id}")

            return PaymentResult(
                success=True,
                payment_id=intent.id,
                external_id=intent.id,
                client_secret=intent.client_secret,
                status=self._map_status(intent.status),
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return PaymentResult(success=False, payment_id="", error=str(e))

    async def confirm_payment(
        self, payment_id: str, payment_method: Optional[str] = None
    ) -> PaymentResult:
        """Confirm a Stripe Payment Intent."""
        try:
            intent = stripe.PaymentIntent.confirm(payment_id, payment_method=payment_method)

            return PaymentResult(
                success=intent.status in ["succeeded", "processing"],
                payment_id=intent.id,
                external_id=intent.id,
                status=self._map_status(intent.status),
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe confirm error: {e}")
            return PaymentResult(success=False, payment_id=payment_id, error=str(e))

    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """Get the status of a Stripe Payment Intent."""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_id)

            return PaymentResult(
                success=True,
                payment_id=intent.id,
                external_id=intent.id,
                status=self._map_status(intent.status),
            )
        except stripe.error.StripeError as e:
            logger.error(f"Stripe status error: {e}")
            return PaymentResult(success=False, payment_id=payment_id, error=str(e))

    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> RefundResult:
        """Refund a Stripe payment."""
        try:
            refund_params = {"payment_intent": payment_id}
            if amount:
                refund_params["amount"] = amount

            refund = stripe.Refund.create(**refund_params)

            return RefundResult(success=True, refund_id=refund.id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {e}")
            return RefundResult(success=False, error=str(e))

    def _map_status(self, stripe_status: str) -> PaymentStatus:
        """Map Stripe status to our PaymentStatus."""
        status_map = {
            "requires_payment_method": PaymentStatus.PENDING,
            "requires_confirmation": PaymentStatus.PENDING,
            "requires_action": PaymentStatus.PROCESSING,
            "processing": PaymentStatus.PROCESSING,
            "requires_capture": PaymentStatus.PROCESSING,
            "succeeded": PaymentStatus.COMPLETED,
            "canceled": PaymentStatus.FAILED,
        }
        return status_map.get(stripe_status, PaymentStatus.PENDING)

    def verify_webhook(self, payload: bytes, signature: str) -> dict:
        """Verify and parse a Stripe webhook event."""
        if not self.webhook_secret:
            raise ValueError("Webhook secret not configured")

        return stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
