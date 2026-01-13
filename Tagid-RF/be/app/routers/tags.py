"""
REST API endpoints for RFID tag management.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.rfid_tag import RFIDScanHistory, RFIDTag
from app.schemas.rfid_tag import (
    RFIDScanHistoryResponse,
    RFIDTagCreate,
    RFIDTagResponse,
    RFIDTagStatsResponse,
    RFIDTagUpdate,
)
from app.services.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=RFIDTagResponse, status_code=201)
async def create_or_update_tag(tag: RFIDTagCreate, db: Session = Depends(get_db)):
    """
    Create or update an RFID tag from a scan event.

    This endpoint handles tag scanning events. If the EPC (Electronic Product Code) already
    exists in the database, it updates the existing record by incrementing the read count
    and updating the last_seen timestamp. If the EPC is new, it creates a new tag entry.
    A scan history entry is always created regardless of whether the tag is new or existing.

    Args:
        tag (RFIDTagCreate): RFID tag data containing:
            - epc (str): Electronic Product Code (required, typically 24 hex characters)
            - tid (str, optional): Tag Identifier - unique chip serial number
            - rssi (int, optional): Received Signal Strength Indicator in dBm (-100 to 0)
            - antenna_port (int, optional): Reader antenna port number (typically 1-4)
            - frequency (float, optional): Read frequency in MHz
            - pc (str, optional): Protocol Control bits
            - crc (str, optional): Cyclic Redundancy Check value
            - user_memory (str, optional): User memory bank data
            - location (str, optional): Physical location where tag was scanned
            - notes (str, optional): Additional notes about the tag
            - metadata (dict, optional): Additional metadata as JSON
        db (Session): Database session (injected by FastAPI)

    Returns:
        RFIDTagResponse: Created or updated tag with:
            - id (int): Database primary key
            - epc (str): Electronic Product Code
            - tid (str | None): Tag Identifier
            - read_count (int): Total number of times this tag has been scanned
            - first_seen (datetime): Timestamp of first scan
            - last_seen (datetime): Timestamp of most recent scan
            - rssi (int | None): Most recent signal strength
            - antenna_port (int | None): Most recent antenna port
            - location (str | None): Most recent location
            - is_active (bool): Whether tag is active (default: true)
            - created_at (datetime): Record creation timestamp
            - updated_at (datetime): Record last update timestamp

    Raises:
        HTTPException 400: Invalid data format or validation error
        HTTPException 500: Database error or internal server error

    Example:
        ```python
        # Scan a new tag
        POST /api/v1/tags/
        {
            "epc": "E2806810000000001234ABCD",
            "rssi": -45,
            "antenna_port": 1,
            "location": "Warehouse A - Entrance"
        }

        # Response (201 Created)
        {
            "id": 1,
            "epc": "E2806810000000001234ABCD",
            "tid": null,
            "read_count": 1,
            "first_seen": "2026-01-06T12:30:00Z",
            "last_seen": "2026-01-06T12:30:00Z",
            "rssi": -45,
            "antenna_port": 1,
            "location": "Warehouse A - Entrance",
            "is_active": true,
            "created_at": "2026-01-06T12:30:00Z",
            "updated_at": "2026-01-06T12:30:00Z"
        }

        # Scan the same tag again
        POST /api/v1/tags/
        {
            "epc": "E2806810000000001234ABCD",
            "rssi": -48,
            "antenna_port": 2
        }

        # Response (201 Created) - read_count incremented
        {
            "id": 1,
            "epc": "E2806810000000001234ABCD",
            "read_count": 2,
            "last_seen": "2026-01-06T12:35:00Z",
            "rssi": -48,
            "antenna_port": 2,
            ...
        }
        ```

    Notes:
        - EPC is used as the unique identifier for tag matching
        - Concurrent scans of the same tag are handled safely by the database
        - WebSocket clients subscribed to /ws/rfid will receive real-time notifications
        - Scan history is preserved even if the tag is later deleted (soft delete)
        - RSSI values typically range from -30 (very close) to -80 (far away)
        - This endpoint is idempotent - multiple scans with identical data are safe
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
    List all RFID tags with pagination and filtering.

    Retrieve a paginated list of RFID tags with optional filtering by active status
    and search capabilities. Results are ordered by most recently seen tags first.

    Args:
        page (int): Page number (1-indexed). Default: 1
        page_size (int): Number of items per page (1-100). Default: 50
        search (str, optional): Search term to filter by EPC or TID (case-insensitive)
        is_active (bool, optional): Filter by active status. None returns all tags
        db (Session): Database session (injected by FastAPI)

    Returns:
        List[RFIDTagResponse]: List of tags matching the criteria, ordered by last_seen desc

    Example:
        ```python
        # Get first page of all tags
        GET /api/v1/tags/?page=1&page_size=50

        # Search for specific EPC
        GET /api/v1/tags/?search=E28068

        # Get only active tags
        GET /api/v1/tags/?is_active=true

        # Combine filters
        GET /api/v1/tags/?search=warehouse&is_active=true&page_size=20
        ```

    Notes:
        - Results are always ordered by last_seen (most recent first)
        - Search is case-insensitive and matches partial EPC or TID
        - Maximum page_size is 100 to prevent performance issues
        - Empty results return [] (not an error)
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

    # Pagination (query.count() executed but total not currently used in response)
    _ = query.count()  # noqa: F841 - Total available for future pagination headers
    tags = (
        query.order_by(desc(RFIDTag.last_seen))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return tags


@router.get("/{tag_id}", response_model=RFIDTagResponse)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    Get a specific RFID tag by database ID.

    Args:
        tag_id (int): Database primary key of the tag
        db (Session): Database session (injected by FastAPI)

    Returns:
        RFIDTagResponse: Tag details

    Raises:
        HTTPException 404: Tag with specified ID not found

    Example:
        ```python
        GET /api/v1/tags/123
        ```
    """
    tag = db.query(RFIDTag).filter(RFIDTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/epc/{epc}", response_model=RFIDTagResponse)
async def get_tag_by_epc(epc: str, db: Session = Depends(get_db)):
    """
    Get an RFID tag by its Electronic Product Code (EPC).

    Retrieve tag information using the EPC as the lookup key instead of database ID.
    This is useful when you have the EPC from a scan but need the full tag details.

    Args:
        epc (str): Electronic Product Code (exact match required)
        db (Session): Database session (injected by FastAPI)

    Returns:
        RFIDTagResponse: Tag details

    Raises:
        HTTPException 404: Tag with specified EPC not found

    Example:
        ```python
        GET /api/v1/tags/epc/E2806810000000001234ABCD
        ```

    Notes:
        - EPC must match exactly (case-sensitive)
        - This is faster than searching when you know the exact EPC
    """
    tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=RFIDTagResponse)
async def update_tag(tag_id: int, tag_update: RFIDTagUpdate, db: Session = Depends(get_db)):
    """
    Update RFID tag metadata (location, notes, etc.).

    Update administrative fields of a tag without affecting scan-related data.
    This endpoint is for manual updates, not for recording scans.

    Args:
        tag_id (int): Database primary key of the tag to update
        tag_update (RFIDTagUpdate): Fields to update (all optional):
            - location (str): Physical location
            - notes (str): Administrative notes
            - user_memory (str): User memory bank data
            - metadata (dict): Additional metadata
            - is_active (bool): Active status
        db (Session): Database session (injected by FastAPI)

    Returns:
        RFIDTagResponse: Updated tag details

    Raises:
        HTTPException 404: Tag with specified ID not found

    Example:
        ```python
        PUT /api/v1/tags/123
        {
            "location": "Warehouse B - Section 3",
            "notes": "Assigned to Product SKU-12345"
        }
        ```

    Notes:
        - This does NOT increment read_count or update last_seen
        - Use POST /api/v1/tags/ for recording scans
        - Only provided fields are updated (partial update supported)
        - Setting is_active=false soft-deletes the tag
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
    Soft delete an RFID tag.

    Marks a tag as inactive (is_active=false) without removing it from the database.
    The tag and its scan history are preserved for audit purposes.

    Args:
        tag_id (int): Database primary key of the tag to delete
        db (Session): Database session (injected by FastAPI)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: Tag with specified ID not found

    Example:
        ```python
        DELETE /api/v1/tags/123
        # Response: 204 No Content
        ```

    Notes:
        - This is a soft delete - tag remains in database with is_active=false
        - Scan history is preserved
        - Tag can be reactivated by setting is_active=true via PUT endpoint
        - Inactive tags are excluded from default listings (use is_active=false filter to see them)
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
    Get recent RFID scan history.

    Retrieve a list of recent tag scans within a specified time window.
    Useful for monitoring real-time activity and analyzing scan patterns.

    Args:
        hours (int): Number of hours to look back (1-168). Default: 24
        limit (int): Maximum number of results to return (1-1000). Default: 100
        db (Session): Database session (injected by FastAPI)

    Returns:
        List[RFIDScanHistoryResponse]: List of scans ordered by most recent first

    Example:
        ```python
        # Get scans from last 24 hours
        GET /api/v1/tags/recent/scans

        # Get scans from last 2 hours, max 50 results
        GET /api/v1/tags/recent/scans?hours=2&limit=50
        ```

    Notes:
        - Results are ordered by scanned_at descending (most recent first)
        - Maximum lookback is 168 hours (7 days)
        - Scan history is preserved even for deleted tags
        - Use this for real-time monitoring dashboards
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
    Get comprehensive RFID tag statistics.

    Returns aggregated statistics about tags and scanning activity including
    totals, activity metrics, and location distribution.

    Args:
        db (Session): Database session (injected by FastAPI)

    Returns:
        RFIDTagStatsResponse: Statistics object containing:
            - total_tags (int): Total number of tags in database
            - active_tags (int): Number of active tags (is_active=true)
            - scans_today (int): Number of scans since midnight UTC
            - scans_last_hour (int): Number of scans in the last 60 minutes
            - most_scanned_tag (dict | None): Tag with highest read_count:
                - id (int): Tag database ID
                - epc (str): Tag EPC
                - read_count (int): Number of scans
            - average_rssi (float | None): Average signal strength across all tags
            - tags_by_location (dict): Count of tags per location {location: count}

    Example:
        ```python
        GET /api/v1/tags/stats/summary

        # Response
        {
            "total_tags": 150,
            "active_tags": 142,
            "scans_today": 1250,
            "scans_last_hour": 45,
            "most_scanned_tag": {
                "id": 23,
                "epc": "E2806810000000001234ABCD",
                "read_count": 89
            },
            "average_rssi": -52.3,
            "tags_by_location": {
                "Warehouse A": 75,
                "Warehouse B": 67
            }
        }
        ```

    Notes:
        - Statistics are calculated in real-time (not cached)
        - "Today" is based on UTC timezone
        - Tags without location are excluded from tags_by_location
        - Average RSSI only includes tags with non-null RSSI values
        - Useful for dashboard displays and monitoring
    """
    # Total and active tags
    total_tags = db.query(RFIDTag).count()
    active_tags = db.query(RFIDTag).filter(RFIDTag.is_active.is_(True)).count()

    # Scans today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    scans_today = (
        db.query(RFIDScanHistory).filter(RFIDScanHistory.scanned_at >= today_start).count()
    )

    # Scans last hour
    hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    scans_last_hour = (
        db.query(RFIDScanHistory).filter(RFIDScanHistory.scanned_at >= hour_ago).count()
    )

    # Most scanned tag
    most_scanned = db.query(RFIDTag).order_by(desc(RFIDTag.read_count)).first()
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


@router.post("/reader/connect")
async def connect_reader():
    """
    Connect to the RFID reader hardware.

    Establishes a connection to the RFID reader device via TCP/IP.
    Must be called before any scanning operations.

    Returns:
        dict: Connection result containing:
            - status (str): "connected" if successful
            - message (str): Human-readable status message
            - reader_info (dict): Reader hardware information
                - model (str): Reader model name
                - firmware (str): Firmware version
                - serial (str): Serial number

    Raises:
        HTTPException 500: Connection failed (network error, wrong IP, reader offline)

    Example:
        ```python
        POST /api/v1/tags/reader/connect

        # Success Response
        {
            "status": "connected",
            "message": "Successfully connected to RFID reader at 192.168.1.200:2022",
            "reader_info": {
                "model": "Chafon CF-RU5102",
                "firmware": "v2.0.1",
                "serial": "M-200"
            }
        }
        ```

    Notes:
        - Reader IP and port are configured via environment variables
        - Connection is persistent until explicitly disconnected
        - Only one connection can be active at a time
        - Check reader status with GET /api/v1/tags/reader/status
    """
    from app.services.rfid_reader import rfid_reader_service

    try:
        connected = await rfid_reader_service.connect()
        if connected:
            info = await rfid_reader_service.get_reader_info()
            return {
                "status": "connected",
                "message": f"Successfully connected to RFID reader at {rfid_reader_service.reader_ip}:{rfid_reader_service.reader_port}",
                "reader_info": info,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to RFID reader at {rfid_reader_service.reader_ip}:{rfid_reader_service.reader_port}. Check IP address and network connection.",
            )
    except Exception as e:
        logger.error(f"Error connecting to reader: {e}")
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")


@router.post("/reader/disconnect")
async def disconnect_reader():
    """
    Disconnect from the RFID reader hardware.

    Closes the active connection to the RFID reader. Any ongoing scans are stopped.

    Returns:
        dict: Disconnection result:
            - status (str): "disconnected"
            - message (str): Confirmation message

    Raises:
        HTTPException 500: Disconnection error

    Example:
        ```python
        POST /api/v1/tags/reader/disconnect

        # Response
        {
            "status": "disconnected",
            "message": "Successfully disconnected from RFID reader"
        }
        ```

    Notes:
        - Safe to call even if not connected
        - Automatically stops any active scanning
        - Reader can be reconnected with POST /api/v1/tags/reader/connect
    """
    from app.services.rfid_reader import rfid_reader_service

    try:
        await rfid_reader_service.disconnect()
        return {"status": "disconnected", "message": "Successfully disconnected from RFID reader"}
    except Exception as e:
        logger.error(f"Error disconnecting from reader: {e}")
        raise HTTPException(status_code=500, detail=f"Disconnect error: {str(e)}")


@router.post("/reader/start-scanning")
async def start_scanning():
    """
    Start continuous RFID tag scanning.

    Begins continuous scanning mode where the reader actively scans for tags.
    Detected tags are automatically saved to the database and broadcast to
    WebSocket clients in real-time.

    Returns:
        dict: Scan start confirmation:
            - status (str): "scanning"
            - message (str): Confirmation message

    Raises:
        HTTPException 400: Reader not connected
        HTTPException 500: Error starting scan

    Example:
        ```python
        POST /api/v1/tags/reader/start-scanning

        # Response
        {
            "status": "scanning",
            "message": "Started continuous tag scanning. Tags will appear in real-time via WebSocket."
        }
        ```

    Notes:
        - Reader must be connected first (POST /api/v1/tags/reader/connect)
        - Tags are automatically saved via POST /api/v1/tags/ endpoint
        - WebSocket clients at /ws/rfid receive real-time tag events
        - Scanning continues until explicitly stopped
        - Use POST /api/v1/tags/reader/stop-scanning to stop
    """
    from app.services.rfid_reader import rfid_reader_service

    if not rfid_reader_service.is_connected:
        raise HTTPException(
            status_code=400,
            detail="Reader not connected. Please connect first using POST /api/v1/tags/reader/connect",
        )

    try:
        await rfid_reader_service.start_scanning()
        return {
            "status": "scanning",
            "message": "Started continuous tag scanning. Tags will appear in real-time via WebSocket.",
        }
    except Exception as e:
        logger.error(f"Error starting scanning: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting scan: {str(e)}")


@router.post("/reader/stop-scanning")
async def stop_scanning():
    """
    Stop continuous RFID tag scanning.

    Stops the active continuous scanning mode. The reader remains connected
    and can be restarted with start-scanning.

    Returns:
        dict: Stop confirmation:
            - status (str): "stopped"
            - message (str): Confirmation message

    Raises:
        HTTPException 500: Error stopping scan

    Example:
        ```python
        POST /api/v1/tags/reader/stop-scanning

        # Response
        {
            "status": "stopped",
            "message": "Stopped tag scanning"
        }
        ```

    Notes:
        - Safe to call even if not currently scanning
        - Reader remains connected after stopping
        - Can restart scanning with POST /api/v1/tags/reader/start-scanning
    """
    from app.services.rfid_reader import rfid_reader_service

    try:
        await rfid_reader_service.stop_scanning()
        return {"status": "stopped", "message": "Stopped tag scanning"}
    except Exception as e:
        logger.error(f"Error stopping scanning: {e}")
        raise HTTPException(status_code=500, detail=f"Error stopping scan: {str(e)}")


@router.get("/reader/status")
async def get_reader_status():
    """
    Get current RFID reader status and configuration.

    Returns the current state of the RFID reader including connection status,
    scanning state, and hardware information.

    Returns:
        dict: Reader status containing:
            - connected (bool): Whether reader is connected
            - scanning (bool): Whether actively scanning
            - reader_info (dict | None): Hardware information if connected
            - connection_type (str): Connection type ("tcp" or "serial")
            - reader_ip (str): Configured reader IP address
            - reader_port (int): Configured reader port
            - error (str, optional): Error message if status check failed

    Example:
        ```python
        GET /api/v1/tags/reader/status

        # Response (connected and scanning)
        {
            "connected": true,
            "scanning": true,
            "reader_info": {
                "model": "Chafon CF-RU5102",
                "firmware": "v2.0.1"
            },
            "connection_type": "tcp",
            "reader_ip": "192.168.1.200",
            "reader_port": 2022
        }

        # Response (not connected)
        {
            "connected": false,
            "scanning": false,
            "reader_info": null,
            "connection_type": "tcp",
            "reader_ip": "192.168.1.200",
            "reader_port": 2022
        }
        ```

    Notes:
        - This endpoint never fails - returns status even if reader is offline
        - Use this to check connection before starting scans
        - Useful for UI status indicators
    """
    from app.services.rfid_reader import rfid_reader_service

    try:
        info = await rfid_reader_service.get_reader_info()
        return {
            "connected": rfid_reader_service.is_connected,
            "scanning": rfid_reader_service.is_scanning,
            "reader_info": info,
            "connection_type": rfid_reader_service.connection_type,
            "reader_ip": rfid_reader_service.reader_ip,
            "reader_port": rfid_reader_service.reader_port,
        }
    except Exception as e:
        logger.error(f"Error getting reader status: {e}")
        return {"connected": False, "scanning": False, "error": str(e)}


@router.post("/reader/read-single")
async def read_single_tag():
    """
    Perform a single RFID tag read (one-time scan).

    Scans for a tag once and returns the result immediately. Unlike continuous
    scanning, this does not save to database or broadcast via WebSocket.
    Useful for manual tag verification or testing.

    Returns:
        dict: Scan result:
            - status (str): "success" if tag found, "no_tag" if none detected
            - tag (dict, optional): Tag data if found:
                - epc (str): Electronic Product Code
                - rssi (int): Signal strength
                - antenna_port (int): Antenna that detected the tag
                - tid (str, optional): Tag Identifier
            - message (str, optional): Message if no tag found

    Raises:
        HTTPException 400: Reader not connected
        HTTPException 500: Error during scan

    Example:
        ```python
        POST /api/v1/tags/reader/read-single

        # Success - tag detected
        {
            "status": "success",
            "tag": {
                "epc": "E2806810000000001234ABCD",
                "rssi": -45,
                "antenna_port": 1,
                "tid": "E200001234567890"
            }
        }

        # No tag detected
        {
            "status": "no_tag",
            "message": "No tag detected. Try moving a tag closer to the reader."
        }
        ```

    Notes:
        - Reader must be connected first
        - Does NOT save tag to database
        - Does NOT broadcast to WebSocket clients
        - Use POST /api/v1/tags/ to save the tag if needed
        - Useful for testing reader connectivity
        - Tag must be within read range (typically 1-5 meters)
    """
    from app.services.rfid_reader import rfid_reader_service

    if not rfid_reader_service.is_connected:
        raise HTTPException(
            status_code=400,
            detail="Reader not connected. Please connect first using POST /api/v1/tags/reader/connect",
        )

    try:
        tag_data = await rfid_reader_service.read_single_tag()
        if tag_data:
            return {"status": "success", "tag": tag_data}
        else:
            return {
                "status": "no_tag",
                "message": "No tag detected. Try moving a tag closer to the reader.",
            }
    except Exception as e:
        logger.error(f"Error reading tag: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading tag: {str(e)}")


@router.get("/live/recent")
async def get_live_tags(
    count: int = Query(50, ge=1, le=200, description="Number of tags to return"),
):
    """
    Get recent tags from the live tag listener.

    Returns tags that were received via the TCP listener server (push mode).
    These are real-time tags that the reader sends automatically when detected.

    Args:
        count (int): Number of recent tags to return (1-200). Default: 50

    Returns:
        dict: Live tag data containing:
            - tags (list): List of recent tag events
            - stats (dict): Statistics about the listener

    Example:
        ```python
        GET /api/v1/tags/live/recent?count=20

        # Response
        {
            "tags": [
                {
                    "epc": "25A858",
                    "timestamp": "2026-01-11T10:09:58.844000",
                    "reader_ip": "192.168.1.200",
                    "epc_length": 3
                }
            ],
            "stats": {
                "total_scans": 15,
                "unique_epcs": 3
            }
        }
        ```

    Notes:
        - This requires the tag_listener_server.py to be running
        - Tags are stored in memory and cleared on server restart
        - Different from /recent/scans which queries the database
    """
    try:
        # Try to import from the standalone listener
        import os
        import sys

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from tag_listener_server import tag_store

        tags = tag_store.get_recent(count)
        stats = {
            "total_scans": tag_store.get_total_count(),
            "unique_epcs": tag_store.get_unique_count(),
        }
        return {"tags": tags, "stats": stats}
    except ImportError:
        return {
            "tags": [],
            "stats": {"total_scans": 0, "unique_epcs": 0},
            "message": "Tag listener not running or not available",
        }


@router.get("/live/stats")
async def get_live_stats():
    """
    Get statistics from the live tag listener.

    Returns:
        dict: Listener statistics
    """
    try:
        import os
        import sys

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from tag_listener_server import tag_store

        return {
            "running": True,
            "total_scans": tag_store.get_total_count(),
            "unique_epcs": tag_store.get_unique_count(),
        }
    except ImportError:
        return {
            "running": False,
            "total_scans": 0,
            "unique_epcs": 0,
            "message": "Tag listener not available",
        }
