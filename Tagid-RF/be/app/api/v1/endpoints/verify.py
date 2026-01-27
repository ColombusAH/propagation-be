import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.db.dependencies import get_db
from prisma import Prisma

logger = logging.getLogger(__name__)

router = APIRouter()


class ProductListResponse(BaseModel):
    """Response for product listing."""
    id: str
    name: str
    price: float
    sku: Optional[str] = None
    description: Optional[str] = None


class ProductVerificationResponse(BaseModel):
    """Response for product verification."""

    is_authentic: bool
    epc: str
    product_description: Optional[str] = None
    manufacturer: Optional[str] = None
    production_date: Optional[str] = None
    kosher_info: Optional[str] = None
    originality_certificate: Optional[str] = None
    message: str


@router.get("/", response_model=List[ProductListResponse])
async def list_all_products(db: Prisma = Depends(get_db)):
    """List all available products."""
    try:
        products = await db.product.find_many(take=100)
        return [
            ProductListResponse(
                id=p.id,
                name=p.name,
                price=p.price,
                sku=p.sku,
                description=p.description
            )
            for p in products
        ]
    except Exception as e:
        logger.error(f"Error in list_all_products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify/{tag_id}", response_model=ProductVerificationResponse)
async def verify_product(tag_id: str, db: Prisma = Depends(get_db)) -> ProductVerificationResponse:
    """
    Public API for verifying product authenticity.

    Consumers can scan an RFID tag and verify if the product is genuine.

    Args:
        tag_id: The EPC or unique identifier of the RFID tag.
    """
    try:
        # Try to find by EPC
        tag = await db.rfidtag.find_unique(where={"epc": tag_id})

        if not tag:
            # Try by ID
            tag = await db.rfidtag.find_unique(where={"id": tag_id})

        if not tag:
            return ProductVerificationResponse(
                is_authentic=False,
                epc=tag_id,
                message="מוצר לא נמצא במערכת. ייתכן שהמוצר אינו מקורי.",
            )

        # Check tag status
        if tag.status == "STOLEN" or tag.status == "DAMAGED":
            return ProductVerificationResponse(
                is_authentic=False,
                epc=tag.epc,
                product_description=tag.productDescription,
                message="אזהרה: מוצר זה דווח כגנוב או פגום!",
            )

        # Product is authentic
        return ProductVerificationResponse(
            is_authentic=True,
            epc=tag.epc,
            product_description=tag.productDescription,
            manufacturer=tag.manufacturer if hasattr(tag, "manufacturer") else None,
            production_date=(
                tag.productionDate.isoformat()
                if hasattr(tag, "productionDate") and tag.productionDate
                else None
            ),
            kosher_info=tag.kosherInfo if hasattr(tag, "kosherInfo") else None,
            originality_certificate=(
                tag.originalityCert if hasattr(tag, "originalityCert") else None
            ),
            message="מוצר מקורי ומאומת ✓",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/{qr_code}")
async def verify_by_qr(qr_code: str, db: Prisma = Depends(get_db)) -> ProductVerificationResponse:
    """
    Verify product by QR code (encrypted).

    Args:
        qr_code: The encrypted QR code content.
    """
    try:
        from app.services.tag_encryption import get_encryption_service

        encrypt_svc = get_encryption_service()

        # Try to decrypt QR code
        try:
            decrypted = encrypt_svc.decrypt_qr(qr_code)
        except Exception:
            return ProductVerificationResponse(
                is_authentic=False,
                epc=qr_code[:20] + "...",
                message="קוד QR לא תקין או לא מזוהה.",
            )

        # Look up by decrypted EPC
        return await verify_product(decrypted, db=db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
