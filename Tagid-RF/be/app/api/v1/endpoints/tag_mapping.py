"""
API routes for Tag Mapping and Encryption.

Provides endpoints for:
- Creating encrypted QR from UHF tag
- Verifying QR ↔ UHF tag match
- Lookup by EPC or QR
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.services.tag_encryption import get_encryption_service, TagEncryptionService
from app.db.prisma import prisma_client
from app.api.dependencies.auth import get_current_user
from app.core.permissions import requires_any_role
from prisma.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tag-mapping", tags=["tag-mapping"])


# Request/Response models
class CreateMappingRequest(BaseModel):
    """Request to create a new tag-QR mapping."""
    epc: str
    product_id: Optional[str] = None
    container_id: Optional[str] = None


class MappingResponse(BaseModel):
    """Response with tag mapping details."""
    id: str
    epc: str
    encrypted_qr: str
    epc_hash: Optional[str]
    product_id: Optional[str]
    container_id: Optional[str]
    is_active: bool


class VerifyRequest(BaseModel):
    """Request to verify EPC-QR match."""
    epc: str
    qr_code: str


class VerifyResponse(BaseModel):
    """Response from verification."""
    match: bool
    epc: Optional[str] = None
    message: str


class DecryptRequest(BaseModel):
    """Request to decrypt a QR code."""
    qr_code: str


class DecryptResponse(BaseModel):
    """Response from decryption."""
    success: bool
    epc: Optional[str] = None
    product_id: Optional[str] = None
    container_id: Optional[str] = None
    error: Optional[str] = None


def get_encryption() -> TagEncryptionService:
    """Dependency to get encryption service."""
    return get_encryption_service()


@router.post("/create", response_model=MappingResponse)
async def create_mapping(
    request: CreateMappingRequest,
    encryption: TagEncryptionService = Depends(get_encryption),
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER"]))
):
    """
    Create a new encrypted QR code for a UHF tag EPC.
    
    **Requires**: STORE_MANAGER role or higher.
    
    - Encrypts the EPC into a unique QR code
    - Saves the mapping to the database
    - Returns the encrypted QR code for printing/display
    """
    # Check if EPC already mapped
    existing = await prisma_client.client.tagmapping.find_unique(
        where={"epc": request.epc}
    )
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"EPC already mapped. Use PUT to update."
        )
    
    # Encrypt the EPC
    encrypted_qr = encryption.encrypt_tag(request.epc)
    epc_hash = encryption.generate_hash(request.epc)
    
    # Save to database
    mapping = await prisma_client.client.tagmapping.create(
        data={
            "epc": request.epc,
            "encryptedQr": encrypted_qr,
            "epcHash": epc_hash,
            "productId": request.product_id,
            "containerId": request.container_id,
            "isActive": True
        }
    )
    
    logger.info(f"Created mapping for EPC: {request.epc[:8]}...")
    
    return MappingResponse(
        id=mapping.id,
        epc=mapping.epc,
        encrypted_qr=mapping.encryptedQr,
        epc_hash=mapping.epcHash,
        product_id=mapping.productId,
        container_id=mapping.containerId,
        is_active=mapping.isActive
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_match(
    request: VerifyRequest,
    encryption: TagEncryptionService = Depends(get_encryption)
):
    """
    Verify if an EPC tag matches a QR code.
    
    Used when scanning both UHF tag and QR code to confirm they 
    represent the same item.
    """
    match = encryption.verify_match(request.epc, request.qr_code)
    
    if match:
        return VerifyResponse(
            match=True,
            epc=request.epc,
            message="QR code and UHF tag match!"
        )
    else:
        return VerifyResponse(
            match=False,
            message="QR code and UHF tag do NOT match"
        )


@router.post("/decrypt", response_model=DecryptResponse)
async def decrypt_qr(
    request: DecryptRequest,
    encryption: TagEncryptionService = Depends(get_encryption)
):
    """
    Decrypt a QR code to get the original EPC and related info.
    
    Also looks up the mapping in the database for product/container info.
    """
    epc = encryption.decrypt_qr(request.qr_code)
    
    if not epc:
        return DecryptResponse(
            success=False,
            error="Failed to decrypt QR code - invalid or corrupted"
        )
    
    # Look up in database for additional info
    mapping = await prisma_client.client.tagmapping.find_unique(
        where={"epc": epc}
    )
    
    if mapping:
        return DecryptResponse(
            success=True,
            epc=epc,
            product_id=mapping.productId,
            container_id=mapping.containerId
        )
    else:
        return DecryptResponse(
            success=True,
            epc=epc,
            error="EPC decrypted but no mapping found in database"
        )


@router.get("/by-epc/{epc}", response_model=MappingResponse)
async def get_by_epc(epc: str):
    """Get mapping by EPC value."""
    mapping = await prisma_client.client.tagmapping.find_unique(
        where={"epc": epc}
    )
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    return MappingResponse(
        id=mapping.id,
        epc=mapping.epc,
        encrypted_qr=mapping.encryptedQr,
        epc_hash=mapping.epcHash,
        product_id=mapping.productId,
        container_id=mapping.containerId,
        is_active=mapping.isActive
    )


@router.get("/by-qr/{qr_code:path}", response_model=MappingResponse)
async def get_by_qr(qr_code: str):
    """Get mapping by encrypted QR code."""
    mapping = await prisma_client.client.tagmapping.find_unique(
        where={"encryptedQr": qr_code}
    )
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    return MappingResponse(
        id=mapping.id,
        epc=mapping.epc,
        encrypted_qr=mapping.encryptedQr,
        epc_hash=mapping.epcHash,
        product_id=mapping.productId,
        container_id=mapping.containerId,
        is_active=mapping.isActive
    )


@router.delete("/{mapping_id}")
async def delete_mapping(
    mapping_id: str,
    current_user: User = Depends(get_current_user),
    _: None = Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER"]))
):
    """
    Delete a tag mapping.
    
    **Requires**: STORE_MANAGER role or higher.
    """
    try:
        await prisma_client.client.tagmapping.delete(
            where={"id": mapping_id}
        )
        return {"message": "Mapping deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Mapping not found")


@router.get("/list", response_model=List[MappingResponse])
async def list_mappings(skip: int = 0, take: int = 50):
    """List all tag mappings with pagination."""
    mappings = await prisma_client.client.tagmapping.find_many(
        skip=skip,
        take=take,
        order={"createdAt": "desc"}
    )
    
    return [
        MappingResponse(
            id=m.id,
            epc=m.epc,
            encrypted_qr=m.encryptedQr,
            epc_hash=m.epcHash,
            product_id=m.productId,
            container_id=m.containerId,
            is_active=m.isActive
        )
        for m in mappings
    ]


@router.post("/simulate-scan")
async def simulate_scan(epc: str = "E2806810000000001234FAKE"):
    """
    Simulate a tag scan event for development/testing.
    Triggering this will broadcast the scan via WebSockets as if the hardware reader read it.
    """
    from app.services.rfid_reader import rfid_reader_service
    
    # Fake tag data
    fake_tag = {
        "epc": epc,
        "rssi": -55.0,
        "antenna_port": 1,
        "pc": 3000,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    logger.info(f"Simulating scan via API: {epc}")
    await rfid_reader_service._process_tag(fake_tag)
    
    return {"status": "scanned", "epc": epc}
