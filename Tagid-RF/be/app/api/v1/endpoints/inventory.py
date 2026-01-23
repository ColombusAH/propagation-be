"""API endpoints for inventory management."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api import deps
from app.services import inventory as inventory_service

router = APIRouter()


class TagData(BaseModel):
    """Tag data for snapshot."""

    epc: str
    rssi: Optional[int] = None


class SnapshotRequest(BaseModel):
    """Request to create inventory snapshot."""

    reader_id: str
    tags: List[TagData]


class SnapshotResponse(BaseModel):
    """Response after creating snapshot."""

    snapshot_id: str
    item_count: int


class StockSummary(BaseModel):
    """Current stock summary."""

    totalItems: int
    readerCount: int
    readers: List[dict]


@router.post("/snapshot", response_model=SnapshotResponse)
async def create_inventory_snapshot(
    request: SnapshotRequest,
    current_user: Any = Depends(deps.get_current_active_user),
) -> SnapshotResponse:
    """
    Create an inventory snapshot for a reader.
    """
    tags = [{"epc": t.epc, "rssi": t.rssi} for t in request.tags]

    snapshot_id = await inventory_service.take_snapshot(
        reader_id=request.reader_id,
        tags=tags,
    )

    if not snapshot_id:
        raise HTTPException(status_code=500, detail="Failed to create snapshot")

    return SnapshotResponse(
        snapshot_id=snapshot_id,
        item_count=len(request.tags),
    )


@router.get("/stock", response_model=StockSummary)
async def get_current_stock(
    store_id: Optional[str] = None,
    current_user: Any = Depends(deps.get_current_active_user),
) -> StockSummary:
    """
    Get current stock levels across all readers.
    """
    stock = await inventory_service.get_current_stock(store_id=store_id)
    return StockSummary(**stock)


@router.get("/snapshot/{reader_id}")
async def get_latest_snapshot(
    reader_id: str,
    current_user: Any = Depends(deps.get_current_active_user),
) -> dict:
    """
    Get the latest inventory snapshot for a reader.
    """
    snapshot = await inventory_service.get_latest_snapshot(reader_id)

    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot found")

    return snapshot


@router.get("/history/{reader_id}")
async def get_inventory_history(
    reader_id: str,
    limit: int = 10,
    current_user: Any = Depends(deps.get_current_active_user),
) -> List[dict]:
    """
    Get inventory snapshot history for a reader.
    """
    return await inventory_service.get_inventory_history(
        reader_id=reader_id,
        limit=limit,
    )
