"""Cash/Manual payment gateway for in-store cash payments."""

import logging
import uuid
from typing import Optional

from .base import (PaymentGateway, PaymentProvider, PaymentRequest,
                   PaymentResult, PaymentStatus, RefundResult)

logger = logging.getLogger(__name__)


class CashGateway(PaymentGateway):
    """Cash payment gateway for manual/in-store payments."""

    @property
    def provider(self) -> PaymentProvider:
        return PaymentProvider.CASH

    async def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a cash payment record (pending until confirmed)."""
        payment_id = f"cash_{uuid.uuid4().hex[:8]}"

        logger.info(f"Created cash payment: {payment_id} for order {request.order_id}")

        return PaymentResult(
            success=True,
            payment_id=payment_id,
            external_id=None,
            status=PaymentStatus.PENDING,
        )

    async def confirm_payment(
        self, payment_id: str, payment_method: Optional[str] = None
    ) -> PaymentResult:
        """Confirm a cash payment (called when cash is received)."""
        logger.info(f"Confirmed cash payment: {payment_id}")

        return PaymentResult(
            success=True, payment_id=payment_id, status=PaymentStatus.COMPLETED
        )

    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """Get cash payment status (would query DB in real implementation)."""
        return PaymentResult(
            success=True, payment_id=payment_id, status=PaymentStatus.PENDING
        )

    async def refund_payment(
        self, payment_id: str, amount: Optional[int] = None
    ) -> RefundResult:
        """Refund a cash payment (manual process)."""
        logger.info(f"Cash refund requested for: {payment_id}")

        return RefundResult(success=True, refund_id=f"refund_{uuid.uuid4().hex[:8]}")
