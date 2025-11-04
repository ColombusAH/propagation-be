"""
REST API endpoints for RFID tag management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional, List
from datetime import datetime, timedelta
from app.services.database import get_db
from app.models.rfid_tag import RFIDTag, RFIDScanHistory
from app.schemas.rfid_tag import (
    RFIDTagCreate,
    RFIDTagUpdate,
    RFIDTagResponse,
    RFIDScanHistoryResponse,
    RFIDTagStatsResponse,
)
from datetime import timezone

router = APIRouter()


@router.post("/", response_model=RFIDTagResponse, status_code=201)
async def create_or_update_tag(tag: RFIDTagCreate, db: Session = Depends(get_db)):
    """
    Create or update a tag.
    
    If EPC already exists, update the existing record (increment read_count,
    update last_seen, etc.). Otherwise, create a new tag.
    Always creates a new entry in scan history.
    """
    # Check if tag with this EPC already exists
    existing = db.query(RFIDTag).filter(RFIDTag.epc == tag.epc).first()
    
    if existing:
        # Update existing tag
        existing.read_count += 1
        existing.last_seen = datetime.now(timezone.utc)
        if tag.rssi is not None:
            existing.rssi = tag.rssi
        if tag.antenna_port is not None:
            existing.antenna_port = tag.antenna_port
        if tag.frequency is not None:
            existing.frequency = tag.frequency
        if tag.location:
            existing.location = tag.location
        if tag.tid:
            existing.tid = tag.tid
        if tag.pc:
            existing.pc = tag.pc
        if tag.crc:
            existing.crc = tag.crc
        if tag.user_memory:
            existing.user_memory = tag.user_memory
        if tag.metadata:
            existing.metadata = tag.metadata
        
        db.commit()
        db.refresh(existing)
        
        # Record in history
        history = RFIDScanHistory(
            epc=tag.epc,
            tid=tag.tid,
            rssi=tag.rssi,
            antenna_port=tag.antenna_port,
            frequency=tag.frequency,
            location=tag.location,
            metadata=tag.metadata,
            scanned_at=datetime.now(timezone.utc),
        )
        db.add(history)
        db.commit()
        
        return existing
    else:
        # Create new tag
        new_tag = RFIDTag(
            epc=tag.epc,
            tid=tag.tid,
            user_memory=tag.user_memory,
            rssi=tag.rssi,
            antenna_port=tag.antenna_port,
            frequency=tag.frequency,
            pc=tag.pc,
            crc=tag.crc,
            metadata=tag.metadata,
            location=tag.location,
            notes=tag.notes,
        )
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)
        
        # Record in history
        history = RFIDScanHistory(
            epc=tag.epc,
            tid=tag.tid,
            rssi=tag.rssi,
            antenna_port=tag.antenna_port,
            frequency=tag.frequency,
            location=tag.location,
            metadata=tag.metadata,
            scanned_at=datetime.now(timezone.utc),
        )
        db.add(history)
        db.commit()
        
        return new_tag


@router.get("/", response_model=List[RFIDTagResponse])
async def list_tags(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by EPC or TID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    """
    List all tags with pagination.
    
    Supports filtering by active status and searching by EPC or TID.
    """
    query = db.query(RFIDTag)
    
    # Filter by active status
    if is_active is not None:
        query = query.filter(RFIDTag.is_active == is_active)
    
    # Search by EPC or TID
    if search:
        query = query.filter(
            (RFIDTag.epc.ilike(f"%{search}%")) | (RFIDTag.tid.ilike(f"%{search}%"))
        )
    
    # Pagination
    total = query.count()
    tags = query.order_by(desc(RFIDTag.last_seen)).offset((page - 1) * page_size).limit(page_size).all()
    
    return tags


@router.get("/{tag_id}", response_model=RFIDTagResponse)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    Get a specific tag by ID.
    """
    tag = db.query(RFIDTag).filter(RFIDTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/epc/{epc}", response_model=RFIDTagResponse)
async def get_tag_by_epc(epc: str, db: Session = Depends(get_db)):
    """
    Get a tag by EPC.
    """
    tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=RFIDTagResponse)
async def update_tag(tag_id: int, tag_update: RFIDTagUpdate, db: Session = Depends(get_db)):
    """
    Update tag metadata (location, notes, etc.).
    
    Note: This does NOT increment read_count. Use POST /tags/ for scanning.
    """
    tag = db.query(RFIDTag).filter(RFIDTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Update fields if provided
    if tag_update.location is not None:
        tag.location = tag_update.location
    if tag_update.notes is not None:
        tag.notes = tag_update.notes
    if tag_update.user_memory is not None:
        tag.user_memory = tag_update.user_memory
    if tag_update.metadata is not None:
        tag.metadata = tag_update.metadata
    if tag_update.is_active is not None:
        tag.is_active = tag_update.is_active
    
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a tag (set is_active=false).
    """
    tag = db.query(RFIDTag).filter(RFIDTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    tag.is_active = False
    db.commit()
    return None


@router.get("/recent/scans", response_model=List[RFIDScanHistoryResponse])
async def get_recent_scans(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: Session = Depends(get_db),
):
    """
    Get recent scan history.
    
    Returns scans from the last N hours.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    scans = (
        db.query(RFIDScanHistory)
        .filter(RFIDScanHistory.scanned_at >= since)
        .order_by(desc(RFIDScanHistory.scanned_at))
        .limit(limit)
        .all()
    )
    return scans


@router.get("/stats/summary", response_model=RFIDTagStatsResponse)
async def get_tag_stats(db: Session = Depends(get_db)):
    """
    Get tag statistics.
    
    Returns:
    - Total tags
    - Active tags
    - Scans today
    - Scans last hour
    - Most scanned tag
    - Average RSSI
    - Tags by location
    """
    # Total and active tags
    total_tags = db.query(RFIDTag).count()
    active_tags = db.query(RFIDTag).filter(RFIDTag.is_active == True).count()
    
    # Scans today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    scans_today = db.query(RFIDScanHistory).filter(RFIDScanHistory.scanned_at >= today_start).count()
    
    # Scans last hour
    hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    scans_last_hour = db.query(RFIDScanHistory).filter(RFIDScanHistory.scanned_at >= hour_ago).count()
    
    # Most scanned tag
    most_scanned = (
        db.query(RFIDTag)
        .order_by(desc(RFIDTag.read_count))
        .first()
    )
    most_scanned_data = None
    if most_scanned:
        most_scanned_data = {
            "id": most_scanned.id,
            "epc": most_scanned.epc,
            "read_count": most_scanned.read_count,
        }
    
    # Average RSSI
    avg_rssi_result = db.query(func.avg(RFIDTag.rssi)).filter(RFIDTag.rssi.isnot(None)).scalar()
    average_rssi = float(avg_rssi_result) if avg_rssi_result else None
    
    # Tags by location
    location_counts = (
        db.query(RFIDTag.location, func.count(RFIDTag.id))
        .filter(RFIDTag.location.isnot(None))
        .group_by(RFIDTag.location)
        .all()
    )
    tags_by_location = {loc: count for loc, count in location_counts if loc}
    
    return RFIDTagStatsResponse(
        total_tags=total_tags,
        active_tags=active_tags,
        scans_today=scans_today,
        scans_last_hour=scans_last_hour,
        most_scanned_tag=most_scanned_data,
        average_rssi=average_rssi,
        tags_by_location=tags_by_location,
    )


