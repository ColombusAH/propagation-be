from typing import List, Optional
from pydantic import BaseModel, Field

# Shared models
class CartItem(BaseModel):
    epc: str = Field(..., description="Electronic Product Code of the tag")
    product_name: str = Field(..., description="Name of the product")
    product_sku: str = Field(..., description="SKU of the product")
    price_cents: int = Field(..., description="Price in cents/agorot")
    image_url: Optional[str] = None

class CartSummary(BaseModel):
    items: List[CartItem]
    total_items: int
    total_price_cents: int
    currency: str = "ILS"

class AddToCartRequest(BaseModel):
    qr_data: str = Field(..., description="Data scanned from the QR code (e.g., tagid://product/SKU-123 or encrypted EPC)")

class CheckoutRequest(BaseModel):
    payment_method_id: str = Field(..., description="Stripe PaymentMethod ID")
    email: Optional[str] = None

class CheckoutResponse(BaseModel):
    status: str
    transaction_id: str
    message: str
