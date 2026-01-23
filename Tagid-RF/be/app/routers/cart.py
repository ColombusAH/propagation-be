import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.rfid_tag import RFIDTag
from app.schemas.cart import (
    AddToCartRequest,
    CartItem,
    CartSummary,
    CheckoutRequest,
    CheckoutResponse,
)
from app.services.database import get_db
from app.services.payment.base import PaymentRequest, PaymentStatus
from app.services.payment.factory import get_gateway

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# Simple in-memory cart storage for demo purposes (keyed by user_id/session)
# In production, this should be in Redis or DB
# Structure: { "session_id": [CartItem, ...] }
FAKE_CART_DB: Dict[str, List[CartItem]] = {}


# Helper to get cart for current session (simulated)
def get_cart_session(session_id: str = "demo_guest"):
    if session_id not in FAKE_CART_DB:
        FAKE_CART_DB[session_id] = []
    return FAKE_CART_DB[session_id]


@router.post("/add", response_model=CartSummary)
async def add_to_cart(request: AddToCartRequest, db: Session = Depends(get_db)):
    """
    Add an item to the cart by scanning its QR code.
    Supports 'tagid://product/{sku}' or direct EPC mapping.
    """
    cart = get_cart_session()

    # Logic to parse QR data
    # Case 1: deep link regex "tagid://product/(.*)"
    # Case 2: encrypted EPC string

    sku = None
    if request.qr_data.startswith("tagid://product/"):
        sku = request.qr_data.replace("tagid://product/", "")
    else:
        # Assume it's an EPC or requires lookup (TODO: Encryption support)
        # For phase 3 simple flow, we assume it's a raw EPC or we find an available tag for the SKU
        pass

    target_tag = None

    if sku:
        # Find an AVAILABLE (unpaid) tag for this SKU
        # Strategy: Pick the first available tag for this product to assign to this cart
        target_tag = (
            db.query(RFIDTag)
            .filter(
                RFIDTag.product_sku == sku,
                RFIDTag.is_paid.is_(False),
                RFIDTag.is_active.is_(True),
            )
            .first()
        )
    else:
        # Try to find by EPC if qr_data is EPC
        target_tag = (
            db.query(RFIDTag)
            .filter(
                RFIDTag.epc == request.qr_data,
                RFIDTag.is_paid.is_(False),
                RFIDTag.is_active.is_(True),
            )
            .first()
        )

    if not target_tag:
        raise HTTPException(
            status_code=404,
            detail="Product not available or already sold. Please try another item.",
        )

    # Check if already in cart
    if any(item.epc == target_tag.epc for item in cart):
        raise HTTPException(status_code=400, detail="Item already in cart")

    # Add to cart
    item = CartItem(
        epc=target_tag.epc,
        product_name=target_tag.product_name or "Unknown Item",
        product_sku=target_tag.product_sku or "UNKNOWN",
        price_cents=target_tag.price_cents or 0,
    )
    cart.append(item)

    return _calculate_summary(cart)


@router.get("/", response_model=CartSummary)
async def view_cart():
    """Get current cart summary."""
    cart = get_cart_session()
    return _calculate_summary(cart)


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(request: CheckoutRequest, db: Session = Depends(get_db)):
    """
    Process checkout using configured Payment Provider (Stripe/Tranzila).
    1. Calculate total
    2. Create PaymentIntent (confirm immediately)
    3. Mark tags as PAID in DB
    4. Clear cart
    """
    cart = get_cart_session()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    summary = _calculate_summary(cart)
    total_amount = summary.total_price_cents

    if total_amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid total amount")

    try:
        # Get configured payment gateway
        # Ideally, provider is selected by client or config.
        # Using default "stripe" or based on settings
        provider_name = (
            settings.DEFAULT_PAYMENT_PROVIDER.lower()
            if hasattr(settings, "DEFAULT_PAYMENT_PROVIDER")
            else "stripe"
        )
        gateway = get_gateway(provider_name)

        # 1. Create Payment
        payment_req = PaymentRequest(
            order_id=f"order_{len(cart)}_{total_amount}",  # Simple ID generation
            amount=total_amount,
            currency="ILS",
            metadata={"items": str([i.product_sku for i in cart])},
            customer_email="guest@example.com",  # TODO: from auth
        )

        payment_res = await gateway.create_payment(payment_req)

        if not payment_res.success:
            raise HTTPException(
                status_code=400, detail=f"Payment creation failed: {payment_res.error}"
            )

        # 2. Confirm Payment (if necessary/supported by gateway in this flow)
        # Note: Some gateways return success immediately (redirect), others need confirmation
        # For Stripe, we emulate the client confirmation or server-side confirm if we have a method

        final_status = payment_res.status
        external_id = payment_res.payment_id

        if request.payment_method_id and provider_name == "stripe":
            # If client provided a payment method (e.g. from frontend Stripe Elements), confirm it
            confirm_res = await gateway.confirm_payment(
                payment_id=payment_res.payment_id,
                payment_method=request.payment_method_id,
            )
            if not confirm_res.success:
                raise HTTPException(status_code=400, detail=f"Payment failed: {confirm_res.error}")
            final_status = confirm_res.status
            external_id = confirm_res.external_id or confirm_res.payment_id

        # Determine if success
        if final_status not in [
            PaymentStatus.COMPLETED,
            PaymentStatus.PROCESSING,
            PaymentStatus.PENDING,
        ]:
            # PENDING might be OK for redirect flows (Tranzila), but for direct checkout we might want completion
            # For now, let's assume PENDING is acceptable for redirect, COMPLETED for direct
            # If it's failed, raise error
            if final_status == PaymentStatus.FAILED:
                raise HTTPException(status_code=400, detail="Payment failed")

        # 3. Success! Mark items as PAID
        for item in cart:
            tag = db.query(RFIDTag).filter(RFIDTag.epc == item.epc).first()
            if tag:
                tag.is_paid = True
                # Optional: tag.sold_at = datetime.now()

        db.commit()

        # 4. Clear Cart
        cart.clear()

        return CheckoutResponse(
            status="success",
            transaction_id=external_id,
            message="Payment successful! You may now exit the store.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _calculate_summary(cart: List[CartItem]) -> CartSummary:
    total = sum(item.price_cents for item in cart)
    return CartSummary(items=cart, total_items=len(cart), total_price_cents=total, currency="ILS")
