"""
Tag Registration API Endpoints

Provides endpoints for:
- Registering scanned tags
- Generating and retrieving QR codes for tags
- Linking tags to products
"""

import base64
import hashlib
import io
import logging
from typing import Optional

import qrcode
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.db.dependencies import get_db
from prisma import Prisma

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tags", tags=["Tag Registration"])


# === Pydantic Models ===


class TagRegisterRequest(BaseModel):
    """Request to register a new tag"""

    epc: str
    store_id: Optional[str] = None


class TagRegisterResponse(BaseModel):
    """Response after registering a tag"""

    id: str
    epc: str
    qr_code: str  # Base64 encoded QR image
    status: str


class TagLinkProductRequest(BaseModel):
    """Request to link a tag to a product"""

    product_id: str


class TagResponse(BaseModel):
    """Tag details response"""

    id: str
    epc: str
    status: str
    qr_code: Optional[str] = None
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    is_paid: bool


class ProductCreateRequest(BaseModel):
    """Request to create a new product"""

    name: str
    price: float
    sku: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    store_id: str


class ProductResponse(BaseModel):
    """Product details response"""

    id: str
    name: str
    price: float
    sku: Optional[str] = None
    category: Optional[str] = None


# === Helper Functions ===


def generate_qr_code(data: str) -> str:
    """Generate a QR code as base64-encoded PNG"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{base64_img}"


def generate_encrypted_qr_data(epc: str, tag_id: str) -> str:
    """Generate encrypted QR data for a tag"""
    # Simple hash-based approach for POC
    combined = f"{epc}:{tag_id}"
    hash_value = hashlib.sha256(combined.encode()).hexdigest()[:16]
    return f"RFID:{hash_value}"


# === API Endpoints ===


@router.post("/register", response_model=TagRegisterResponse)
async def register_tag(request: TagRegisterRequest, db: Prisma = Depends(get_db)):
    """
    Register a scanned RFID tag and generate its QR code.

    Flow:
    1. Check if tag already exists
    2. If new, create tag with UNREGISTERED status
    3. Generate QR code
    4. Return tag details with QR
    """
    logger.info(f"Registering tag with EPC: {request.epc}")

    # Check if tag exists
    existing_tag = await db.rfidtag.find_unique(where={"epc": request.epc})

    if existing_tag:
        # Return existing tag with its QR
        if not existing_tag.encryptedQr:
            # Generate QR if missing
            qr_data = generate_encrypted_qr_data(request.epc, existing_tag.id)
            qr_image = generate_qr_code(qr_data)

            await db.rfidtag.update(where={"id": existing_tag.id}, data={"encryptedQr": qr_data})
        else:
            qr_image = generate_qr_code(existing_tag.encryptedQr)

        return TagRegisterResponse(
            id=existing_tag.id, epc=existing_tag.epc, qr_code=qr_image, status=existing_tag.status
        )

    # Create new tag
    import uuid

    tag_id = str(uuid.uuid4())
    qr_data = generate_encrypted_qr_data(request.epc, tag_id)
    qr_image = generate_qr_code(qr_data)

    new_tag = await db.rfidtag.create(
        data={
            "id": tag_id,
            "epc": request.epc,
            "encryptedQr": qr_data,
            "status": "UNREGISTERED",
            "isActive": True,
            "isPaid": False,
        }
    )

    logger.info(f"Created new tag: {new_tag.id}")

    return TagRegisterResponse(
        id=new_tag.id, epc=new_tag.epc, qr_code=qr_image, status=new_tag.status
    )


# === Product Endpoints ===


@router.post("/products", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest, db: Prisma = Depends(get_db)):
    """Create a new product for tag linking"""
    product = await db.product.create(
        data={
            "name": request.name,
            "price": request.price,
            "sku": request.sku,
            "category": request.category,
            "description": request.description,
            "storeId": request.store_id,
        }
    )

    return ProductResponse(
        id=product.id,
        name=product.name,
        price=product.price,
        sku=product.sku,
        category=product.category,
    )


@router.get("/products/store/{store_id}")
async def list_products(store_id: str, db: Prisma = Depends(get_db)):
    """List all products in a store"""
    products = await db.product.find_many(where={"storeId": store_id})

    return [
        ProductResponse(id=p.id, name=p.name, price=p.price, sku=p.sku, category=p.category)
        for p in products
    ]


@router.get("/unregistered")
async def list_unregistered_tags(db: Prisma = Depends(get_db)):
    """List all tags that need to be linked to products"""
    tags = await db.rfidtag.find_many(
        where={"status": "UNREGISTERED"}, order_by={"createdAt": "desc"}, take=50
    )

    return [
        TagResponse(
            id=tag.id,
            epc=tag.epc,
            status=tag.status,
            qr_code=None,  # Don't include QR in list for performance
            product_id=tag.productId,
            product_name=tag.productDescription,
            product_price=None,
            is_paid=tag.isPaid,
        )
        for tag in tags
    ]


@router.get("/{tag_id}/qr")
async def get_tag_qr(tag_id: str, db: Prisma = Depends(get_db)):
    """Get the QR code for a specific tag"""
    tag = await db.rfidtag.find_unique(where={"id": tag_id})

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    if not tag.encryptedQr:
        # Generate QR if missing
        qr_data = generate_encrypted_qr_data(tag.epc, tag.id)
        qr_image = generate_qr_code(qr_data)

        await db.rfidtag.update(where={"id": tag.id}, data={"encryptedQr": qr_data})
    else:
        qr_image = generate_qr_code(tag.encryptedQr)

    return {"qr_code": qr_image}


@router.post("/{tag_id}/link-product", response_model=TagResponse)
async def link_tag_to_product(
    tag_id: str, request: TagLinkProductRequest, db: Prisma = Depends(get_db)
):
    """
    Link a registered tag to a product.
    Changes tag status from UNREGISTERED to REGISTERED.
    """
    tag = await db.rfidtag.find_unique(where={"id": tag_id})

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    # Verify product exists
    product = await db.product.find_unique(where={"id": request.product_id})

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Update tag with product info
    updated_tag = await db.rfidtag.update(
        where={"id": tag_id},
        data={"productId": product.id, "productDescription": product.name, "status": "REGISTERED"},
    )

    logger.info(f"Linked tag {tag_id} to product {product.id}")

    return TagResponse(
        id=updated_tag.id,
        epc=updated_tag.epc,
        status=updated_tag.status,
        qr_code=generate_qr_code(updated_tag.encryptedQr) if updated_tag.encryptedQr else None,
        product_id=product.id,
        product_name=product.name,
        product_price=product.price,
        is_paid=updated_tag.isPaid,
    )


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: str, db: Prisma = Depends(get_db)):
    """Get tag details by ID"""
    tag = await db.rfidtag.find_unique(where={"id": tag_id})

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    product = None
    if tag.productId:
        product = await db.product.find_unique(where={"id": tag.productId})

    return TagResponse(
        id=tag.id,
        epc=tag.epc,
        status=tag.status,
        qr_code=generate_qr_code(tag.encryptedQr) if tag.encryptedQr else None,
        product_id=tag.productId,
        product_name=product.name if product else None,
        product_price=product.price if product else None,
        is_paid=tag.isPaid,
    )
