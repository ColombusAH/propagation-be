from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api import deps
from app.db.prisma import prisma_client

router = APIRouter()


class QRResponse(BaseModel):
    """QR code data response."""

    slug: str
    entry_url: str
    name: str
    qr_type: str  # "network" or "store"


class StoreListItem(BaseModel):
    """Store item in list."""

    id: str
    name: str
    slug: str
    address: str | None
    entry_url: str


@router.get("/qr", response_model=QRResponse)
async def get_network_qr(
    current_user: Any = Depends(deps.get_current_active_user),
) -> QRResponse:
    """
    Get the Network Entry QR code data for the user's business.
    """
    try:
        async with prisma_client.client as db:
            if not current_user.businessId:
                raise HTTPException(status_code=400, detail="User not part of a business")

            business = await db.business.find_unique(where={"id": current_user.businessId})

            if not business:
                raise HTTPException(status_code=404, detail="Business not found")

            entry_url = f"https://app.tagid.com/enter/{business.slug}"

            return QRResponse(
                slug=business.slug,
                entry_url=entry_url,
                name=business.name,
                qr_type="network",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores", response_model=List[StoreListItem])
async def get_stores_list(
    current_user: Any = Depends(deps.get_current_active_user),
) -> List[StoreListItem]:
    """
    Get all stores for the user's business with their QR codes.
    """
    try:
        async with prisma_client.client as db:
            if not current_user.businessId:
                raise HTTPException(status_code=400, detail="User not part of a business")

            stores = await db.store.find_many(
                where={"businessId": current_user.businessId, "isActive": True}
            )

            return [
                StoreListItem(
                    id=store.id,
                    name=store.name,
                    slug=store.slug,
                    address=store.address,
                    entry_url=f"https://app.tagid.com/store/{store.slug}",
                )
                for store in stores
            ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/store/{store_id}/qr", response_model=QRResponse)
async def get_store_qr(
    store_id: str,
    current_user: Any = Depends(deps.get_current_active_user),
) -> QRResponse:
    """
    Get the QR code data for a specific store.
    """
    try:
        async with prisma_client.client as db:
            store = await db.store.find_unique(where={"id": store_id})

            if not store:
                raise HTTPException(status_code=404, detail="Store not found")

            # Verify user has access to this store's business
            if current_user.businessId != store.businessId:
                raise HTTPException(status_code=403, detail="Access denied")

            entry_url = f"https://app.tagid.com/store/{store.slug}"

            return QRResponse(
                slug=store.slug, entry_url=entry_url, name=store.name, qr_type="store"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
