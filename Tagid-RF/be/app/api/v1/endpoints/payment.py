"""
Payment API endpoints.
Handles payment creation, confirmation, refunds, and status queries.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.core.permissions import requires_any_role
from prisma import Json
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

# from app.services.cash_provider import CashProvider # Migrated to factory
from app.services.nexi_provider import NexiProvider
from app.services.payment.base import PaymentRequest, PaymentStatus

# from app.services.stripe_provider import StripeProvider # Deleted
# from app.services.tranzila_provider import TranzilaProvider # Deleted
from app.services.payment.factory import get_gateway

logger = logging.getLogger(__name__)
router = APIRouter()


# Helper to bridge Enum to factory string
def get_provider_gateway(provider_enum: PaymentProviderEnum):
    if provider_enum == PaymentProviderEnum.NEXI:
        return NexiProvider()
    return get_gateway(provider_enum.value.lower())


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
        try:
            gateway = get_provider_gateway(request.payment_provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment provider: {request.payment_provider}",
            )

        # Create payment intent with provider
        # New Gateway interface uses PaymentRequest object
        # Adapting request...

        # Note: Legacy providers (Nexi) might still use old signature: create_payment_intent(amount, currency, metadata)
        # New Gateway uses: create_payment(PaymentRequest)

        external_id = None
        client_secret = None

        if request.payment_provider == PaymentProviderEnum.NEXI:
            # Legacy path for Nexi
            intent = await gateway.create_payment_intent(
                amount=request.amount,
                currency=request.currency,
                metadata=request.metadata,
            )
            external_id = intent["external_id"]
            client_secret = intent.get("client_secret")
        else:
            # New Factory path
            pay_req = PaymentRequest(
                amount=request.amount,
                currency=request.currency,
                metadata=request.metadata or {},
                order_id=request.order_id,
            )
            result = await gateway.create_payment(pay_req)
            if not result.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment creation failed: {result.error}",
                )
            external_id = result.payment_id
            client_secret = result.client_secret

        # Create payment record in database
        payment = await prisma_client.client.payment.create(
            data={
                "orderId": request.order_id,
                "amount": request.amount,
                "currency": request.currency,
                "provider": request.payment_provider.value,
                "externalId": external_id,
                "status": "PENDING",
                "metadata": Json(request.metadata or {}),
            }
        )

        logger.info(f"Created payment intent {payment.id} for order {request.order_id}")

        return PaymentIntentResponse(
            payment_id=payment.id,
            external_id=external_id,
            client_secret=client_secret,
            amount=request.amount,
            currency=request.currency,
            status=PaymentStatusEnum.PENDING,
            provider=request.payment_provider,
        )

    except HTTPException:
        raise
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
        try:
            provider_enum = PaymentProviderEnum(payment.provider)
            gateway = get_provider_gateway(provider_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment provider: {payment.provider}",
            )

        # Confirm payment with provider
        status_val = PaymentStatusEnum.PENDING
        metadata = {}

        if provider_enum == PaymentProviderEnum.NEXI:
            confirmation = await gateway.confirm_payment(
                payment_id=payment.externalId,
                payment_method_id=request.payment_method_id,
            )
            status_val = confirmation["status"]
            metadata = confirmation.get("metadata")
        else:
            # New Gateway interface
            # Confirm is mostly for Stripe. Tranzila usually confirms via callback or redirect validation.
            # Assuming confirm_payment signature: confirm_payment(payment_id, payment_method)
            result = await gateway.confirm_payment(
                payment_id=payment.externalId, payment_method=request.payment_method_id
            )

            if result.success:
                # Map new status to enum
                # PaymentStatus.COMPLETED -> COMPLETED
                if result.status == PaymentStatus.COMPLETED:
                    status_val = PaymentStatusEnum.COMPLETED
                elif result.status == PaymentStatus.FAILED:
                    status_val = PaymentStatusEnum.FAILED
                else:
                    status_val = PaymentStatusEnum.PENDING
            else:
                status_val = PaymentStatusEnum.FAILED

        # Update payment in database
        await prisma_client.client.payment.update(
            where={"id": payment.id},
            data={
                "status": status_val.value,
                "paidAt": (datetime.now() if status_val == PaymentStatusEnum.COMPLETED else None),
            },
        )

        # If payment completed, mark associated tags as paid
        if status_val == PaymentStatusEnum.COMPLETED:
            await mark_order_tags_as_paid(payment.orderId, payment.id)

        logger.info(f"Confirmed payment {payment.id}, status: {status_val}")

        return PaymentConfirmResponse(
            payment_id=payment.id,
            status=status_val,
            external_id=payment.externalId,
            metadata=metadata,
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
    """
    try:
        gateway = get_gateway("cash")

        # Create cash payment intent
        # New gateway interface
        pay_req = PaymentRequest(
            amount=request.amount,
            currency="ILS",
            metadata={"notes": request.notes},
            order_id=request.order_id,
        )
        result = await gateway.create_payment(pay_req)

        # Create payment record
        payment = await prisma_client.client.payment.create(
            data={
                "orderId": request.order_id,
                "amount": request.amount,
                "currency": "ILS",
                "provider": "CASH",
                "externalId": result.payment_id,
                "status": "PENDING",
                "metadata": {"notes": request.notes},
            }
        )

        logger.info(f"Created cash payment {payment.id} for order {request.order_id}")

        return PaymentIntentResponse(
            payment_id=payment.id,
            external_id=result.payment_id,
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
        try:
            provider_enum = PaymentProviderEnum(payment.provider)
            gateway = get_provider_gateway(provider_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment provider: {payment.provider}",
            )

        # Refund with provider
        refund_id = None
        refund_amount = request.amount

        if provider_enum == PaymentProviderEnum.NEXI:
            refund = await gateway.refund_payment(
                payment_id=payment.externalId, amount=request.amount
            )
            refund_id = refund["refund_id"]
            refund_amount = refund["amount"]
        else:
            # New Gateway
            result = await gateway.refund_payment(
                payment_id=payment.externalId, amount=request.amount
            )
            if not result.success:
                raise HTTPException(status_code=400, detail=f"Refund failed: {result.error}")
            refund_id = result.refund_id
            # Assuming full refund if amount not returned

        # Update payment status
        await prisma_client.client.payment.update(
            where={"id": payment.id}, data={"status": "REFUNDED"}
        )

        # Unmark tags as paid
        await unmark_order_tags_as_paid(payment.orderId)

        logger.info(f"Refunded payment {payment.id}")

        return RefundResponse(
            payment_id=payment.id,
            refund_id=refund_id,
            amount=refund_amount,
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
        # Update tags in RfidTag table
        # We search by paymentId if it was already pre-linked, 
        # or we might need another way to identify which tags belong to this order_id
        # For now, let's assume tags were associated with this order_id during scanning
        # or we link them here if they are 'ACTIVE' and belong to this store
        
        # If order_id is a containerId, we mark tags in that container
        await prisma_client.client.rfidtag.update_many(
            where={
                "OR": [
                    {"containerId": order_id},
                    {"paymentId": order_id} # Fallback if order_id was used as paymentId
                ]
            },
            data={"isPaid": True, "paidAt": datetime.now(), "paymentId": payment_id},
        )
        logger.info(f"Marked tags for order/container {order_id} as paid with payment {payment_id}")
    except Exception as e:
        logger.error(f"Error marking tags as paid: {str(e)}")


async def unmark_order_tags_as_paid(order_id: str):
    """Unmark all tags in an order as paid (for refunds)."""
    try:
        await prisma_client.client.rfidtag.update_many(
            where={"paymentId": order_id},
            data={"isPaid": False, "paidAt": None, "paymentId": None},
        )
        logger.info(f"Unmarked tags for order {order_id} as paid")
    except Exception as e:
        logger.error(f"Error unmarking tags: {str(e)}")
