"""API endpoints for product verification (counterfeit prevention)."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.prisma import prisma_client

router = APIRouter()


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


@router.get("/verify/{tag_id}", response_model=ProductVerificationResponse)
async def verify_product(tag_id: str) -> ProductVerificationResponse:
    """
    Public API for verifying product authenticity.
    
    Consumers can scan an RFID tag and verify if the product is genuine.
    
    Args:
        tag_id: The EPC or unique identifier of the RFID tag.
    """
    try:
        async with prisma_client.client as db:
            # Try to find by EPC
            tag = await db.rfidtag.find_unique(
                where={"epc": tag_id}
            )
            
            if not tag:
                # Try by ID
                tag = await db.rfidtag.find_unique(
                    where={"id": tag_id}
                )
            
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
                manufacturer=tag.manufacturer if hasattr(tag, 'manufacturer') else None,
                production_date=tag.productionDate.isoformat() if hasattr(tag, 'productionDate') and tag.productionDate else None,
                kosher_info=tag.kosherInfo if hasattr(tag, 'kosherInfo') else None,
                originality_certificate=tag.originalityCert if hasattr(tag, 'originalityCert') else None,
                message="מוצר מקורי ומאומת ✓",
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/{qr_code}")
async def verify_by_qr(qr_code: str) -> ProductVerificationResponse:
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
        return await verify_product(decrypted)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
