"""
Cart API endpoints.
Handles shopping cart operations, including QR scan and bulk "Bath" sync.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.db.prisma import prisma_client
from app.schemas.cart import (
    AddToCartRequest,
    CartItem,
    CartSummary,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory cart storage (keyed by user_id)
# In production, this should be in Redis or Database
USER_CARTS: Dict[str, List[CartItem]] = {}


def get_user_cart(user_id: str) -> List[CartItem]:
    if user_id not in USER_CARTS:
        USER_CARTS[user_id] = []
    return USER_CARTS[user_id]


@router.post("/add", response_model=CartSummary)
async def add_to_cart(
    request: AddToCartRequest,
    current_user: Any = Depends(deps.get_current_active_user),
) -> CartSummary:
    """
    Add a single item to the cart via QR scan.
    The QR data can be a direct EPC or an encrypted QR.
    """
    user_id = current_user.id
    cart = get_user_cart(user_id)
    
    qr_data = request.qr_data
    epc = None
    
    # Logic to identify tag from QR
    # 1. Check if it's an encrypted QR (starts with something specific or decryptable)
    try:
        from app.services.tag_encryption import get_encryption_service
        encrypt_svc = get_encryption_service()
        epc = encrypt_svc.decrypt_qr(qr_data)
    except Exception:
        # Fallback: Treat as raw EPC or SKU link
        if qr_data.startswith("tagid://product/"):
            # If it's a SKU link, we need to find an available tag for that SKU
            sku = qr_data.replace("tagid://product/", "")
            async with prisma_client.client as db:
                tag = await db.rfidtag.find_first(
                    where={"productId": sku, "isPaid": False, "status": "ACTIVE"}
                )
                if tag:
                    epc = tag.epc
        else:
            epc = qr_data

    if not epc:
        raise HTTPException(status_code=400, detail="Could not identify product from QR")

    # Verify tag exists and is available
    async with prisma_client.client as db:
        tag = await db.rfidtag.find_unique(where={"epc": epc})
        
        if not tag:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if tag.isPaid:
            raise HTTPException(status_code=400, detail="This item has already been paid for")
            
        if any(item.epc == epc for item in cart):
            raise HTTPException(status_code=400, detail="Item already in cart")

        # Create CartItem
        new_item = CartItem(
            epc=tag.epc,
            product_name=tag.productDescription or "Unknown Product",
            product_sku=tag.productId or "UNKNOWN",
            price_cents=0, # TODO: Add price to RfidTag model
        )
        cart.append(new_item)

    return _calculate_summary(cart)


@router.post("/sync-bath", response_model=CartSummary)
async def sync_bath_cart(
    epcs: List[str],
    current_user: Any = Depends(deps.get_current_active_user),
) -> CartSummary:
    """
    Sync the cart with a bulk scan from the "Bath" reader.
    Replaces current cart items with the scanned tags.
    """
    user_id = current_user.id
    new_cart: List[CartItem] = []
    
    async with prisma_client.client as db:
        for epc in epcs:
            tag = await db.rfidtag.find_unique(where={"epc": epc})
            if tag and not tag.isPaid:
                new_cart.append(CartItem(
                    epc=tag.epc,
                    product_name=tag.productDescription or "Unknown Product",
                    product_sku=tag.productId or "UNKNOWN",
                    price_cents=0,
                ))
            elif tag and tag.isPaid:
                logger.warning(f"Scanned paid tag in bath: {epc}")
            else:
                logger.warning(f"Unknown tag in bath: {epc}")

    USER_CARTS[user_id] = new_cart
    return _calculate_summary(new_cart)


@router.get("/", response_model=CartSummary)
async def view_cart(
    current_user: Any = Depends(deps.get_current_active_user),
) -> CartSummary:
    """View current user's cart."""
    cart = get_user_cart(current_user.id)
    return _calculate_summary(cart)


@router.delete("/clear")
async def clear_cart(
    current_user: Any = Depends(deps.get_current_active_user),
):
    """Empty the current user's cart."""
    USER_CARTS[current_user.id] = []
    return {"message": "Cart cleared"}


def _calculate_summary(cart: List[CartItem]) -> CartSummary:
    total = sum(i.price_cents for i in cart)
    return CartSummary(
        items=cart,
        total_items=len(cart),
        total_price_cents=total,
        currency="ILS"
    )
