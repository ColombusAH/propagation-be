from typing import List, Optional
from pydantic import BaseModel

class ProductSummary(BaseModel):
    product_sku: Optional[str] = None
    product_name: Optional[str] = None
    total_items: int = 0
    available_items: int = 0
    sold_items: int = 0
    price_cents: Optional[int] = None

class InventoryResponse(BaseModel):
    products: List[ProductSummary]
    total_products: int
    total_value_cents: int
