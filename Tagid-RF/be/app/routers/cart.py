import logging
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.database import get_db
from app.models.rfid_tag import RFIDTag
from app.schemas.cart import CartItem, CartSummary, AddToCartRequest, CheckoutRequest, CheckoutResponse
from app.services.stripe_provider import StripeProvider
# from app.services.auth import get_current_user # Todo: Add auth later if needed for guest checkouts

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()
stripe_provider = StripeProvider()

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
        target_tag = db.query(RFIDTag).filter(
            RFIDTag.product_sku == sku,
            RFIDTag.is_paid == False,
            RFIDTag.is_active == True
        ).first()
    else:
        # Try to find by EPC if qr_data is EPC
        target_tag = db.query(RFIDTag).filter(
            RFIDTag.epc == request.qr_data,
            RFIDTag.is_paid == False,
            RFIDTag.is_active == True
        ).first()

    if not target_tag:
        raise HTTPException(
            status_code=404, 
            detail="Product not available or already sold. Please try another item."
        )

    # Check if already in cart
    if any(item.epc == target_tag.epc for item in cart):
        raise HTTPException(status_code=400, detail="Item already in cart")

    # Add to cart
    item = CartItem(
        epc=target_tag.epc,
        product_name=target_tag.product_name or "Unknown Item",
        product_sku=target_tag.product_sku or "UNKNOWN",
        price_cents=target_tag.price_cents or 0
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
    Process checkout using Stripe.
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
        # 1. Create & Confirm Payment via Stripe
        # In a real app, client creates Intent, we confirm, or use 3D Secure
        # For this demo, we assume we get a valid payment_method_id and confirm immediately
        
        # Create Intent
        intent = await stripe_provider.create_payment_intent(
            amount=total_amount,
            currency="ils",
            metadata={"items": str([i.product_sku for i in cart])}
        )
        
        # Confirm (Mocking the client confirmation step for simplicity if PM provided)
        confirm_result = await stripe_provider.confirm_payment(
            payment_id=intent["payment_id"],
            payment_method_id=request.payment_method_id
        )
        
        if confirm_result["status"] != "completed":
             raise HTTPException(status_code=400, detail=f"Payment failed: {confirm_result['status']}")

        # 2. Success! Mark items as PAID
        for item in cart:
            tag = db.query(RFIDTag).filter(RFIDTag.epc == item.epc).first()
            if tag:
                tag.is_paid = True
                # Optional: tag.sold_at = datetime.now()
                
        db.commit()
        
        # 3. Clear Cart
        cart.clear()
        
        return CheckoutResponse(
            status="success",
            transaction_id=intent["external_id"],
            message="Payment successful! You may now exit the store."
        )

    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _calculate_summary(cart: List[CartItem]) -> CartSummary:
    total = sum(item.price_cents for item in cart)
    return CartSummary(
        items=cart,
        total_items=len(cart),
        total_price_cents=total,
        currency="ILS"
    )
