"""
Bath Cart API Endpoints

Provides endpoints for:
- Adding tags to cart when scanned by bath reader
- Getting cart contents
- Processing checkout/payment
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from prisma import Prisma

from app.db.dependencies import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bath", tags=["Bath Cart"])


# ============ Pydantic Models ============


class ScanTagRequest(BaseModel):
    """Request when a tag is scanned by bath reader"""

    epc: str
    reader_id: Optional[str] = None  # If known


class CartItem(BaseModel):
    """Single item in cart"""

    tag_id: str
    epc: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    added_at: str


class CartResponse(BaseModel):
    """Full cart response"""

    bath_id: str
    bath_name: str
    items: list[CartItem]
    total_items: int
    total_price: float


class CheckoutRequest(BaseModel):
    """Checkout request"""

    payment_method: str = "cash"  # cash, card, digital
    customer_id: Optional[str] = None


class CheckoutResponse(BaseModel):
    """Checkout response"""

    success: bool
    order_id: str
    total_price: float
    items_count: int
    message: str


# ============ In-Memory Cart Storage ============
# For POC - in production, use Redis or database

_bath_carts: dict[str, list[str]] = {}  # bath_id -> list of tag_ids


def get_bath_cart(bath_id: str) -> list[str]:
    """Get or create cart for bath"""
    if bath_id not in _bath_carts:
        _bath_carts[bath_id] = []
    return _bath_carts[bath_id]


def clear_bath_cart(bath_id: str):
    """Clear cart after checkout"""
    _bath_carts[bath_id] = []


# ============ API Endpoints ============


@router.post("/{bath_id}/scan", response_model=CartItem)
async def scan_tag_to_cart(bath_id: str, request: ScanTagRequest, db: Prisma = Depends(get_db)):
    """
    Add a tag to the cart when scanned by bath reader.

    Flow:
    1. Verify bath reader exists
    2. Find tag by EPC
    3. Check tag is registered and not paid
    4. Add to cart
    5. Update tag status to IN_CART
    """
    logger.info(f"Bath {bath_id} scanned tag: {request.epc}")

    # Verify bath reader
    reader = await db.rfidreader.find_unique(where={"id": bath_id})
    if not reader:
        # Try by QR code
        reader = await db.rfidreader.find_first(where={"qrCode": bath_id})

    if not reader or reader.type != "BATH":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bath reader not found")

    # Find tag by EPC
    tag = await db.rfidtag.find_unique(where={"epc": request.epc})

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Tag with EPC {request.epc} not found"
        )

    # Check if already paid
    if tag.isPaid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag is already paid")

    # Check if already in cart
    cart = get_bath_cart(reader.id)
    if tag.id in cart:
        logger.info(f"Tag {tag.id} already in cart")
    else:
        # Add to cart
        cart.append(tag.id)

        # Update tag status to IN_CART
        await db.rfidtag.update(where={"id": tag.id}, data={"status": "IN_CART"})
        logger.info(f"Added tag {tag.id} to cart")

    # Get product info if linked
    product = None
    if tag.productId:
        product = await db.product.find_unique(where={"id": tag.productId})

    return CartItem(
        tag_id=tag.id,
        epc=tag.epc,
        product_id=tag.productId,
        product_name=product.name if product else tag.productDescription,
        product_price=product.price if product else None,
        added_at=datetime.now().isoformat(),
    )


@router.delete("/{bath_id}/cart/{tag_id}")
async def remove_from_cart(bath_id: str, tag_id: str, db: Prisma = Depends(get_db)):
    """Remove a tag from the cart"""
    # Verify bath reader
    reader = await db.rfidreader.find_unique(where={"id": bath_id})
    if not reader:
        reader = await db.rfidreader.find_first(where={"qrCode": bath_id})

    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bath reader not found")

    cart = get_bath_cart(reader.id)

    if tag_id in cart:
        cart.remove(tag_id)

        # Update tag status back to REGISTERED
        await db.rfidtag.update(where={"id": tag_id}, data={"status": "REGISTERED"})

        return {"message": "Item removed from cart"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not in cart")


@router.get("/{bath_id}/cart", response_model=CartResponse)
async def get_cart(bath_id: str, db: Prisma = Depends(get_db)):
    """Get current cart contents for a bath reader"""
    # Verify bath reader
    reader = await db.rfidreader.find_unique(where={"id": bath_id})
    if not reader:
        reader = await db.rfidreader.find_first(where={"qrCode": bath_id})

    if not reader or reader.type != "BATH":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bath reader not found")

    cart_tag_ids = get_bath_cart(reader.id)

    items = []
    total_price = 0.0

    for tag_id in cart_tag_ids:
        tag = await db.rfidtag.find_unique(where={"id": tag_id})
        if not tag:
            continue

        product = None
        if tag.productId:
            product = await db.product.find_unique(where={"id": tag.productId})

        price = product.price if product else 0
        total_price += price

        items.append(
            CartItem(
                tag_id=tag.id,
                epc=tag.epc,
                product_id=tag.productId,
                product_name=product.name if product else tag.productDescription,
                product_price=price,
                added_at="",  # Not tracked in simple POC
            )
        )

    return CartResponse(
        bath_id=reader.id,
        bath_name=reader.name,
        items=items,
        total_items=len(items),
        total_price=total_price,
    )


@router.post("/{bath_id}/checkout", response_model=CheckoutResponse)
async def checkout(bath_id: str, request: CheckoutRequest, db: Prisma = Depends(get_db)):
    """
    Process checkout for bath cart.

    Flow:
    1. Get all items in cart
    2. Calculate total
    3. Mark all tags as PAID (isPaid=True, status=SOLD)
    4. Clear cart
    5. Return confirmation
    """
    logger.info(f"Checkout for bath {bath_id}")

    # Verify bath reader
    reader = await db.rfidreader.find_unique(where={"id": bath_id})
    if not reader:
        reader = await db.rfidreader.find_first(where={"qrCode": bath_id})

    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bath reader not found")

    cart_tag_ids = get_bath_cart(reader.id)

    if not cart_tag_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    total_price = 0.0
    items_count = 0

    # Process each item
    for tag_id in cart_tag_ids:
        tag = await db.rfidtag.find_unique(where={"id": tag_id})
        if not tag:
            continue

        # Get price
        if tag.productId:
            product = await db.product.find_unique(where={"id": tag.productId})
            if product:
                total_price += product.price

        # Mark as paid
        await db.rfidtag.update(
            where={"id": tag_id}, data={"isPaid": True, "paidAt": datetime.now(), "status": "SOLD"}
        )
        items_count += 1

    # Generate order ID
    import uuid

    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    # Clear cart
    clear_bath_cart(reader.id)

    logger.info(f"Checkout complete: {order_id}, {items_count} items, ${total_price}")

    return CheckoutResponse(
        success=True,
        order_id=order_id,
        total_price=total_price,
        items_count=items_count,
        message="התשלום בוצע בהצלחה!",
    )


@router.post("/{bath_id}/clear")
async def clear_cart(bath_id: str, db: Prisma = Depends(get_db)):
    """Clear the cart without checkout"""
    # Verify bath reader
    reader = await db.rfidreader.find_unique(where={"id": bath_id})
    if not reader:
        reader = await db.rfidreader.find_first(where={"qrCode": bath_id})

    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bath reader not found")

    cart_tag_ids = get_bath_cart(reader.id)

    # Reset tag statuses
    for tag_id in cart_tag_ids:
        await db.rfidtag.update(where={"id": tag_id}, data={"status": "REGISTERED"})

    clear_bath_cart(reader.id)

    return {"message": "Cart cleared"}
