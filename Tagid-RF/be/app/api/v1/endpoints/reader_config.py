"""
Reader Configuration API Endpoints

Provides endpoints for:
- Listing RFID readers
- Configuring readers as bath/gate type
- Generating QR codes for bath identification
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

router = APIRouter(prefix="/readers", tags=["Reader Configuration"])


# === Pydantic Models ===


class ReaderResponse(BaseModel):
    """Reader details response"""

    id: str
    name: str
    ip_address: str
    location: Optional[str] = None
    type: str
    status: str
    qr_code: Optional[str] = None
    store_id: Optional[str] = None


class SetBathRequest(BaseModel):
    """Request to configure reader as bath"""

    name: Optional[str] = None  # Optional rename


class BathQrResponse(BaseModel):
    """Response with bath QR code"""

    reader_id: str
    reader_name: str
    qr_code: str
    qr_data: str


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


def generate_bath_qr_data(reader_id: str) -> str:
    """Generate unique QR data for bath identification"""
    hash_value = hashlib.sha256(reader_id.encode()).hexdigest()[:12]
    return f"BATH:{hash_value}"


# === API Endpoints ===


@router.get("", response_model=list[ReaderResponse])
async def list_readers(store_id: Optional[str] = None, db: Prisma = Depends(get_db)):
    """
    List all RFID readers, optionally filtered by store.
    """
    where_clause = {}
    if store_id:
        where_clause["storeId"] = store_id

    readers = await db.rfidreader.find_many(where=where_clause if where_clause else None)

    return [
        ReaderResponse(
            id=r.id,
            name=r.name,
            ip_address=r.ipAddress,
            location=r.location,
            type=r.type,
            status=r.status,
            qr_code=r.qrCode,
            store_id=r.storeId,
        )
        for r in readers
    ]


@router.get("/{reader_id}", response_model=ReaderResponse)
async def get_reader(reader_id: str, db: Prisma = Depends(get_db)):
    """Get reader details by ID"""
    reader = await db.rfidreader.find_unique(where={"id": reader_id})

    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")

    return ReaderResponse(
        id=reader.id,
        name=reader.name,
        ip_address=reader.ipAddress,
        location=reader.location,
        type=reader.type,
        status=reader.status,
        qr_code=reader.qrCode,
        store_id=reader.storeId,
    )


@router.put("/{reader_id}/set-bath", response_model=BathQrResponse)
async def set_reader_as_bath(reader_id: str, request: SetBathRequest, db: Prisma = Depends(get_db)):
    """
    Configure a reader as a bath (basket) reader.
    Generates a unique QR code for bath identification.
    """
    reader = await db.rfidreader.find_unique(where={"id": reader_id})

    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")

    # Generate unique QR for this bath
    qr_data = generate_bath_qr_data(reader_id)
    qr_image = generate_qr_code(qr_data)

    # Update reader to bath type with QR
    update_data = {"type": "BATH", "qrCode": qr_data}

    if request.name:
        update_data["name"] = request.name

    updated_reader = await db.rfidreader.update(where={"id": reader_id}, data=update_data)

    logger.info(f"Reader {reader_id} configured as BATH with QR: {qr_data}")

    return BathQrResponse(
        reader_id=updated_reader.id,
        reader_name=updated_reader.name,
        qr_code=qr_image,
        qr_data=qr_data,
    )


@router.put("/{reader_id}/set-gate")
async def set_reader_as_gate(reader_id: str, db: Prisma = Depends(get_db)):
    """Configure a reader as a gate (exit) reader."""
    reader = await db.rfidreader.find_unique(where={"id": reader_id})

    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")

    updated_reader = await db.rfidreader.update(
        where={"id": reader_id}, data={"type": "GATE", "qrCode": None}  # Gates don't need QR
    )

    logger.info(f"Reader {reader_id} configured as GATE")

    return {"message": "Reader configured as gate", "reader_id": updated_reader.id}


@router.get("/{reader_id}/qr", response_model=BathQrResponse)
async def get_reader_qr(reader_id: str, db: Prisma = Depends(get_db)):
    """
    Get the QR code for a bath reader.
    Only works for readers configured as BATH type.
    """
    reader = await db.rfidreader.find_unique(where={"id": reader_id})

    if not reader:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reader not found")

    if reader.type != "BATH":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reader is not configured as a bath. Use PUT /set-bath first.",
        )

    if not reader.qrCode:
        # Generate if missing
        qr_data = generate_bath_qr_data(reader_id)
        await db.rfidreader.update(where={"id": reader_id}, data={"qrCode": qr_data})
    else:
        qr_data = reader.qrCode

    qr_image = generate_qr_code(qr_data)

    return BathQrResponse(
        reader_id=reader.id, reader_name=reader.name, qr_code=qr_image, qr_data=qr_data
    )


@router.get("/bath/all")
async def list_bath_readers(db: Prisma = Depends(get_db)):
    """List all readers configured as bath type"""
    readers = await db.rfidreader.find_many(where={"type": "BATH"})

    return [
        ReaderResponse(
            id=r.id,
            name=r.name,
            ip_address=r.ipAddress,
            location=r.location,
            type=r.type,
            status=r.status,
            qr_code=r.qrCode,
            store_id=r.storeId,
        )
        for r in readers
    ]
