from io import BytesIO

import qrcode
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/qr/{sku}", response_class=StreamingResponse)
def generate_product_qr(sku: str):
    """
    Generate a QR code for a specific product SKU.

    The QR code contains a deep link (e.g., tagid://product/SKU-123) that the
    Customer Mobile App can scan to add the item to the cart instantly.
    """
    if not sku:
        raise HTTPException(status_code=400, detail="SKU cannot be empty")

    # Deep link format for the mobile app
    # When scanned, the app will interpret this as "Add product {sku} to cart"
    qr_data = f"tagid://product/{sku}"

    # Generate QR Code
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save to BytesIO to return as response
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        return StreamingResponse(img_buffer, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR: {str(e)}")
