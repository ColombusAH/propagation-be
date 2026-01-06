"""
Payment API endpoints.
Handles payment creation, confirmation, refunds, and status queries.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.core.permissions import requires_any_role
from app.db.prisma import prisma_client
from app.schemas.payment import (
    CashPaymentRequest,
    PaymentConfirmRequest,
    PaymentConfirmResponse,
    PaymentIntentRequest,
    PaymentIntentResponse,
    PaymentProviderEnum,
    PaymentStatusEnum,
    PaymentStatusResponse,
    RefundRequest,
    RefundResponse,
)
from app.services.cash_provider import CashProvider
from app.services.nexi_provider import NexiProvider
from app.services.stripe_provider import StripeProvider
from app.services.tranzila_provider import TranzilaProvider

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize payment providers
payment_providers = {
    PaymentProviderEnum.STRIPE: StripeProvider(),
    PaymentProviderEnum.TRANZILA: TranzilaProvider(),
    PaymentProviderEnum.NEXI: NexiProvider(),
    PaymentProviderEnum.CASH: CashProvider(),
}


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: PaymentIntentRequest, current_user=Depends(get_current_user)
):
    """
    Create a payment intent for an order.

    - **order_id**: Order ID to pay for
    - **amount**: Amount in agorot/cents
    - **currency**: Currency code (default: ILS)
    - **payment_provider**: Payment provider to use
    """
    try:
        # Get payment provider
        provider = payment_providers.get(request.payment_provider)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment provider: {request.payment_provider}",
            )

        # Create payment intent with provider
        intent = await provider.create_payment_intent(
            amount=request.amount, currency=request.currency, metadata=request.metadata
        )

        # Create payment record in database
        payment = await prisma_client.client.payment.create(
            data={
                "orderId": request.order_id,
                "amount": request.amount,
                "currency": request.currency,
                "provider": request.payment_provider.value,
                "externalId": intent["external_id"],
                "status": "PENDING",
                "metadata": request.metadata,
            }
        )

        logger.info(f"Created payment intent {payment.id} for order {request.order_id}")

        return PaymentIntentResponse(
            payment_id=payment.id,
            external_id=intent["external_id"],
            client_secret=intent.get("client_secret"),
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatusEnum.PENDING,
            provider=request.payment_provider,
        )

    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}",
        )


@router.post("/confirm", response_model=PaymentConfirmResponse)
async def confirm_payment(request: PaymentConfirmRequest, current_user=Depends(get_current_user)):
    """
    Confirm a payment.

    - **payment_id**: Payment ID to confirm
    - **payment_method_id**: Payment method ID (for Stripe)
    """
    try:
        # Get payment from database
        payment = await prisma_client.client.payment.find_unique(where={"id": request.payment_id})

        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        # Get payment provider
        provider = payment_providers.get(PaymentProviderEnum(payment.provider))
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment provider: {payment.provider}",
            )

        # Confirm payment with provider
        confirmation = await provider.confirm_payment(
            payment_id=payment.externalId, payment_method_id=request.payment_method_id
        )

        # Update payment in database
        updated_payment = await prisma_client.client.payment.update(
            where={"id": payment.id},
            data={
                "status": confirmation["status"].value,
                "paidAt": (
                    datetime.now()
                    if confirmation["status"] == PaymentStatusEnum.COMPLETED
                    else None
                ),
            },
        )

        # If payment completed, mark associated tags as paid
        if confirmation["status"] == PaymentStatusEnum.COMPLETED:
            await mark_order_tags_as_paid(payment.orderId, payment.id)

        logger.info(f"Confirmed payment {payment.id}, status: {confirmation['status']}")

        return PaymentConfirmResponse(
            payment_id=payment.id,
            status=PaymentStatusEnum(updated_payment.status),
            external_id=payment.externalId,
            metadata=confirmation.get("metadata"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm payment: {str(e)}",
        )


@router.post("/cash", response_model=PaymentIntentResponse)
async def create_cash_payment(
    request: CashPaymentRequest,
    current_user=Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER"])),
):
    """
    Record a cash payment (STORE_MANAGER+ only).

    - **order_id**: Order ID
    - **amount**: Amount in agorot
    - **notes**: Payment notes
    """
    try:
        provider = payment_providers[PaymentProviderEnum.CASH]

        # Create cash payment intent
        intent = await provider.create_payment_intent(
            amount=request.amount, currency="ILS", metadata={"notes": request.notes}
        )

        # Create payment record
        payment = await prisma_client.client.payment.create(
            data={
                "orderId": request.order_id,
                "amount": request.amount,
                "currency": "ILS",
                "provider": "CASH",
                "externalId": intent["external_id"],
                "status": "PENDING",
                "metadata": {"notes": request.notes},
            }
        )

        logger.info(f"Created cash payment {payment.id} for order {request.order_id}")

        return PaymentIntentResponse(
            payment_id=payment.id,
            external_id=intent["external_id"],
            client_secret=None,
            amount=request.amount,
            currency="ILS",
            status=PaymentStatusEnum.PENDING,
            provider=PaymentProviderEnum.CASH,
        )

    except Exception as e:
        logger.error(f"Error creating cash payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create cash payment: {str(e)}",
        )


@router.post("/refund", response_model=RefundResponse)
async def refund_payment(
    request: RefundRequest,
    current_user=Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER"])),
):
    """
    Refund a payment (STORE_MANAGER+ only).

    - **payment_id**: Payment ID to refund
    - **amount**: Amount to refund (None for full refund)
    - **reason**: Refund reason
    """
    try:
        # Get payment
        payment = await prisma_client.client.payment.find_unique(where={"id": request.payment_id})

        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        if payment.status != "COMPLETED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot refund payment with status {payment.status}",
            )

        # Get provider
        provider = payment_providers.get(PaymentProviderEnum(payment.provider))
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment provider: {payment.provider}",
            )

        # Refund with provider
        refund = await provider.refund_payment(payment_id=payment.externalId, amount=request.amount)

        # Update payment status
        await prisma_client.client.payment.update(
            where={"id": payment.id}, data={"status": "REFUNDED"}
        )

        # Unmark tags as paid
        await unmark_order_tags_as_paid(payment.orderId)

        logger.info(f"Refunded payment {payment.id}")

        return RefundResponse(
            payment_id=payment.id,
            refund_id=refund["refund_id"],
            amount=refund["amount"],
            status=PaymentStatusEnum.REFUNDED,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refunding payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refund payment: {str(e)}",
        )


@router.get("/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(payment_id: str, current_user=Depends(get_current_user)):
    """
    Get payment status.

    - **payment_id**: Payment ID
    """
    try:
        payment = await prisma_client.client.payment.find_unique(where={"id": payment_id})

        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        return PaymentStatusResponse(
            payment_id=payment.id,
            status=PaymentStatusEnum(payment.status),
            amount=payment.amount,
            currency=payment.currency,
            provider=PaymentProviderEnum(payment.provider),
            created_at=payment.createdAt,
            paid_at=payment.paidAt,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment status: {str(e)}",
        )


# Helper functions


async def mark_order_tags_as_paid(order_id: str, payment_id: str):
    """Mark all tags in an order as paid."""
    try:
        # This assumes you have an Order model with tags
        # Update based on your actual data model
        await prisma_client.client.tagmapping.update_many(
            where={"orderId": order_id},  # Adjust based on your schema
            data={"isPaid": True, "paidAt": datetime.now(), "paymentId": payment_id},
        )
        logger.info(f"Marked tags for order {order_id} as paid")
    except Exception as e:
        logger.error(f"Error marking tags as paid: {str(e)}")


async def unmark_order_tags_as_paid(order_id: str):
    """Unmark all tags in an order as paid (for refunds)."""
    try:
        await prisma_client.client.tagmapping.update_many(
            where={"orderId": order_id},  # Adjust based on your schema
            data={"isPaid": False, "paidAt": None, "paymentId": None},
        )
        logger.info(f"Unmarked tags for order {order_id} as paid")
    except Exception as e:
        logger.error(f"Error unmarking tags: {str(e)}")
