from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.rfid_tag import RFIDTag
from app.schemas.inventory import InventoryResponse, ProductSummary
from app.services.database import get_db

router = APIRouter()


@router.get("/summary", response_model=InventoryResponse)
def get_inventory_summary(db: Session = Depends(get_db)):
    """
    Get aggregated inventory summary based on RFID tags.
    Groups tags by product SKU/Name and calculates:
    - Total items
    - Available (unpaid)
    - Sold (paid)
    """
    # Group by product_sku and product_name
    # We use product_sku as the primary grouper, but fallback to name if sku is missing
    # To ensure consistent grouping, we might filter out tags with neither

    # Query to aggregate data
    # SELECT product_sku, product_name, price_cents,
    #        COUNT(*) as total,
    #        SUM(CASE WHEN is_paid = FALSE THEN 1 ELSE 0 END) as available,
    #        SUM(CASE WHEN is_paid = TRUE THEN 1 ELSE 0 END) as sold
    # FROM rfid_tags
    # WHERE product_sku IS NOT NULL OR product_name IS NOT NULL
    # GROUP BY product_sku, product_name, price_cents

    results = (
        db.query(
            RFIDTag.product_sku,
            RFIDTag.product_name,
            RFIDTag.price_cents,
            func.count(RFIDTag.id).label("total"),
            func.sum(case((RFIDTag.is_paid.is_(False), 1), else_=0)).label("available"),
            func.sum(case((RFIDTag.is_paid.is_(True), 1), else_=0)).label("sold"),
        )
        .filter((RFIDTag.product_sku.isnot(None)) | (RFIDTag.product_name.isnot(None)))
        .group_by(RFIDTag.product_sku, RFIDTag.product_name, RFIDTag.price_cents)
        .all()
    )

    product_summaries = []
    total_value = 0

    for row in results:
        # row is a keyed tuple
        sku = row.product_sku
        name = row.product_name
        price = row.price_cents or 0
        total = row.total
        available = row.available or 0
        sold = row.sold or 0

        # Calculate value of AVAILABLE items only (usually inventory value refers to asset value)
        total_value += available * price

        product_summaries.append(
            ProductSummary(
                product_sku=sku,
                product_name=name,
                total_items=total,
                available_items=available,
                sold_items=sold,
                price_cents=row.price_cents,
            )
        )

    return InventoryResponse(
        products=product_summaries,
        total_products=len(product_summaries),
        total_value_cents=total_value,
    )
