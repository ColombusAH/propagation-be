"""
Orders API endpoints.
Handles order history and order details for customers.
"""

import logging
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.deps import get_current_user
from app.db.prisma import prisma_client

logger = logging.getLogger(__name__)
router = APIRouter()


class OrderItemResponse(BaseModel):
    """Order item in an order"""
    productId: str
    productName: str
    quantity: int
    priceInCents: int


class OrderResponse(BaseModel):
    """Order response model"""
    id: str
    createdAt: datetime
    status: str
    totalInCents: int
    currency: str
    provider: str
    paymentMethod: str = "Credit Card"
    cardLast4: str = "****"
    items: List[OrderItemResponse] = Field(default_factory=list)


class OrdersListResponse(BaseModel):
    """List of orders response"""
    orders: List[OrderResponse]
    total: int


@router.get("/", response_model=OrdersListResponse)
async def get_user_orders(
    current_user=Depends(get_current_user),
):
    """
    Get all orders for the current user.
    Returns a list of payments associated with the user.
    """
    try:
        # Get all payments for this user
        # Since Payment doesn't have userId, we'll get all payments for now
        # In production, you'd link payments to orders and orders to users
        payments = await prisma_client.client.payment.find_many(
            order={"createdAt": "desc"},
            take=50,  # Limit to last 50 orders
        )
        
        orders = []
        for payment in payments:
            # Build order response
            # Fetch items for each order in the list
            tags = await prisma_client.client.rfidtag.find_many(
                where={"paymentId": payment.id}
            )
            
            items = []
            product_groups = {}
            for tag in tags:
                desc = tag.productDescription or "Unknown Product"
                if desc not in product_groups:
                    product_groups[desc] = {"count": 0}
                product_groups[desc]["count"] += 1
            
            for desc, data in product_groups.items():
                items.append(OrderItemResponse(
                    productId="N/A",
                    productName=desc,
                    quantity=data["count"],
                    priceInCents=0
                ))

            order = OrderResponse(
                id=payment.id,
                createdAt=payment.createdAt,
                status=payment.status,
                totalInCents=payment.amount,
                currency=payment.currency,
                provider=payment.provider,
                items=items,
            )
            orders.append(order)
        
        return OrdersListResponse(
            orders=orders,
            total=len(orders)
        )
        
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orders: {str(e)}"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: str,
    current_user=Depends(get_current_user),
):
    """
    Get details of a specific order.
    """
    try:
        payment = await prisma_client.client.payment.find_unique(
            where={"id": order_id}
        )
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Get items associated with this payment/order
        tags = await prisma_client.client.rfidtag.find_many(
            where={"paymentId": order_id}
        )
        
        items = []
        # Group tags by product description to show quantities
        product_groups = {}
        for tag in tags:
            desc = tag.productDescription or "Unknown Product"
            if desc not in product_groups:
                product_groups[desc] = {"desc": desc, "count": 0, "price": 0}
            product_groups[desc]["count"] += 1
            # Note: We should ideally have price on the tag or product relation
            # For now, we'll estimate or leave as 0 if not available
            
        for desc, data in product_groups.items():
            items.append(OrderItemResponse(
                productId="N/A",
                productName=data["desc"],
                quantity=data["count"],
                priceInCents=0 # Price info needs to be linked better in schema
            ))
            
        return OrderResponse(
            id=payment.id,
            createdAt=payment.createdAt,
            status=payment.status,
            totalInCents=payment.amount,
            currency=payment.currency,
            provider=payment.provider,
            items=items,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order: {str(e)}"
        )
