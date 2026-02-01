"""
Pydantic schemas for RFID tag validation and serialization.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class RFIDTagBase(BaseModel):
    """
    Base schema with common RFID tag fields.

    This schema contains all the core fields that can be read from an RFID tag
    or associated with it during scanning operations.

    Example:
        ```python
        tag = RFIDTagBase(
            epc="E2806810000000001234ABCD",
            tid="E200001234567890",
            rssi=-45,
            antenna_port=1,
            location="Warehouse A - Section 3"
        )
        ```
    """

    epc: str = Field(
        ...,
        max_length=128,
        description="Electronic Product Code - unique identifier for the RFID tag. "
        "Typically 24 hexadecimal characters (96-bit EPC). "
        "Example: 'E2806810000000001234ABCD'",
        examples=["E2806810000000001234ABCD", "E28011700000020123456789"],
    )

    tid: Optional[str] = Field(
        None,
        max_length=128,
        description="Tag Identifier - unique chip serial number burned into the tag at manufacturing. "
        "Cannot be changed. Useful for authentication and anti-counterfeiting. "
        "Example: 'E200001234567890'",
        examples=["E200001234567890", "E280116070000123456789AB"],
    )

    user_memory: Optional[str] = Field(
        None,
        description="User-defined data stored in the tag's user memory bank. "
        "Can contain custom application data, product info, or serialization. "
        "Format and encoding depends on your application.",
        examples=["SKU-12345", "LOT:2024-01-15|BATCH:A123"],
    )

    rssi: Optional[float] = Field(
        None,
        description="Received Signal Strength Indicator in dBm. "
        "Indicates how strong the tag's signal is. "
        "Range: typically -30 (very close) to -80 (far away). "
        "Lower (more negative) = weaker signal = farther away.",
        examples=[-45, -52.5, -68],
        ge=-300,
        le=0,
    )

    antenna_port: Optional[int] = Field(
        None,
        ge=0,
        le=255,
        description="Reader antenna port number that detected the tag (typically 1-4). "
        "Useful for determining tag location based on antenna placement. "
        "Most readers have 1-4 antenna ports.",
        examples=[1, 2, 3, 4],
    )

    frequency: Optional[float] = Field(
        None,
        description="Read frequency in MHz. "
        "UHF RFID typically operates at 860-960 MHz depending on region. "
        "US: 902-928 MHz, EU: 865-868 MHz, China: 920-925 MHz.",
        examples=[915.25, 866.5, 922.75],
        ge=800,
        le=1000,
    )

    pc: Optional[str] = Field(
        None,
        max_length=16,
        description="Protocol Control bits - contains tag configuration info like EPC length. "
        "Usually 4 hex characters. Automatically read from tag.",
        examples=["3000", "3400", "2800"],
    )

    crc: Optional[str] = Field(
        None,
        max_length=16,
        description="Cyclic Redundancy Check - error detection code for data integrity. "
        "Automatically calculated and verified by the reader.",
        examples=["A5B3", "1F2E", "C4D7"],
    )

    meta: Optional[Dict[str, Any]] = Field(
        None,
        serialization_alias="metadata",
        description="Additional custom metadata as JSON object. "
        "Use this for application-specific data that doesn't fit other fields.",
        examples=[
            {"product_id": "SKU-123", "batch": "2024-01"},
            {"zone": "A", "shelf": "3", "bin": "12"},
        ],
    )

    location: Optional[str] = Field(
        None,
        max_length=100,
        description="Physical location where the tag was scanned or is stored. "
        "Free-form text field for human-readable location description.",
        examples=["Warehouse A - Section 3", "Store Floor - Aisle 5", "Loading Dock"],
    )

    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Administrative notes or comments about the tag. "
        "Use for tracking issues, special handling, or other observations.",
        examples=[
            "Assigned to Product SKU-12345",
            "Tag damaged - replace soon",
            "VIP customer item - handle with care",
        ],
    )

    # Product & Payment Info
    product_name: Optional[str] = Field(None, max_length=255, description="Associated product name")
    product_sku: Optional[str] = Field(
        None, max_length=50, description="Product Stock Keeping Unit"
    )
    price_cents: Optional[int] = Field(None, description="Price in cents (e.g., 1000 = 10.00)")
    store_id: Optional[int] = Field(None, description="Store ID this tag belongs to")
    is_paid: bool = Field(False, description="Payment status")


class RFIDTagCreate(RFIDTagBase):
    """
    Schema for creating a new RFID tag or recording a scan event.

    Inherits all fields from RFIDTagBase. Use this when:
    - Recording a new tag scan
    - Manually registering a tag
    - Importing tags from external systems

    Only the `epc` field is required. All other fields are optional.

    Example:
        ```python
        # Minimal tag creation
        tag = RFIDTagCreate(epc="E2806810000000001234ABCD")

        # Full tag data from scan
        tag = RFIDTagCreate(
            epc="E2806810000000001234ABCD",
            tid="E200001234567890",
            rssi=-45,
            antenna_port=1,
            frequency=915.25,
            location="Warehouse A"
        )
        ```
    """


class RFIDTagUpdate(BaseModel):
    """
    Schema for updating RFID tag metadata.

    Use this for administrative updates to tag information.
    All fields are optional - only provide fields you want to update.

    Note:
        This does NOT update scan-related data (rssi, read_count, etc.).
        Use POST /api/v1/tags/ for recording scans.

    Example:
        ```python
        # Update location only
        update = RFIDTagUpdate(location="Warehouse B - Section 5")

        # Update multiple fields
        update = RFIDTagUpdate(
            location="Store Floor",
            notes="Moved to retail display",
            is_active=True
        )

        # Soft delete (deactivate)
        update = RFIDTagUpdate(is_active=False)
        ```
    """

    location: Optional[str] = Field(
        None, max_length=100, description="Update the physical location"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Update administrative notes")
    user_memory: Optional[str] = Field(None, description="Update user-defined data")
    meta: Optional[Dict[str, Any]] = Field(
        None, serialization_alias="metadata", description="Update custom metadata"
    )
    is_active: Optional[bool] = Field(None, description="Set to false to soft-delete the tag")

    # Product updates
    product_name: Optional[str] = Field(None, max_length=255)
    product_sku: Optional[str] = Field(None, max_length=50)
    price_cents: Optional[int] = Field(None)
    store_id: Optional[int] = Field(None)
    is_paid: Optional[bool] = Field(None)


class RFIDTagResponse(RFIDTagBase):
    """
    Schema for RFID tag API responses.

    Includes all base fields plus database-generated fields like ID,
    timestamps, and read statistics.

    This is what you receive when:
    - Creating/updating a tag (POST /api/v1/tags/)
    - Retrieving tags (GET /api/v1/tags/)
    - Getting a specific tag (GET /api/v1/tags/{id})

    Example Response:
        ```json
        {
            "id": 123,
            "epc": "E2806810000000001234ABCD",
            "tid": "E200001234567890",
            "rssi": -45,
            "antenna_port": 1,
            "location": "Warehouse A",
            "read_count": 5,
            "is_active": true,
            "first_seen": "2026-01-06T10:00:00Z",
            "last_seen": "2026-01-06T12:00:00Z",
            "created_at": "2026-01-06T10:00:00Z",
            "updated_at": "2026-01-06T12:00:00Z"
        }
        ```
    """

    id: int = Field(description="Database primary key")
    read_count: int = Field(description="Total number of times this tag has been scanned")
    is_active: bool = Field(description="Whether the tag is active (false = soft deleted)")
    first_seen: datetime = Field(description="Timestamp of first scan")
    last_seen: datetime = Field(description="Timestamp of most recent scan")
    created_at: datetime = Field(description="Database record creation timestamp")
    updated_at: datetime = Field(description="Database record last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class RFIDScanHistoryResponse(BaseModel):
    """
    Schema for RFID scan history records.

    Represents a single scan event in the history. Each scan creates
    a new history entry, even for the same tag.

    Use this to:
    - Track scan patterns over time
    - Analyze tag movement
    - Monitor reader performance
    - Audit tag activity

    Example Response:
        ```json
        {
            "id": 456,
            "epc": "E2806810000000001234ABCD",
            "tid": "E200001234567890",
            "rssi": -48,
            "antenna_port": 2,
            "frequency": 915.25,
            "location": "Warehouse A",
            "reader_id": "M-200",
            "metadata": {"zone": "A"},
            "scanned_at": "2026-01-06T12:35:00Z"
        }
        ```
    """

    id: int = Field(description="Scan history record ID")
    epc: str = Field(description="Electronic Product Code of scanned tag")
    tid: Optional[str] = Field(description="Tag Identifier if available")
    rssi: Optional[float] = Field(description="Signal strength at time of scan")
    antenna_port: Optional[int] = Field(description="Antenna that detected the tag")
    frequency: Optional[float] = Field(description="Frequency used for this scan")
    location: Optional[str] = Field(description="Location at time of scan")
    reader_id: Optional[str] = Field(description="Identifier of the reader device")
    meta: Optional[Dict[str, Any]] = Field(
        alias="metadata",
        serialization_alias="metadata",
        description="Additional scan metadata",
    )
    scanned_at: datetime = Field(description="Exact timestamp when tag was scanned")

    model_config = ConfigDict(from_attributes=True)


class RFIDTagStatsResponse(BaseModel):
    """
    Schema for RFID tag statistics response.

    Provides aggregated statistics about tags and scanning activity.
    All statistics are calculated in real-time.

    Returned by: GET /api/v1/tags/stats/summary

    Example Response:
        ```json
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
                "Warehouse B": 67,
                "Store Floor": 8
            }
        }
        ```
    """

    total_tags: int = Field(description="Total number of tags in database")
    active_tags: int = Field(description="Number of active tags (is_active=true)")
    scans_today: int = Field(description="Number of scans since midnight UTC")
    scans_last_hour: int = Field(description="Number of scans in the last 60 minutes")
    most_scanned_tag: Optional[Dict[str, Any]] = Field(
        description="Tag with highest read_count. Contains: id, epc, read_count"
    )
    average_rssi: Optional[float] = Field(
        description="Average signal strength across all tags with RSSI data"
    )
    tags_by_location: Dict[str, int] = Field(
        description="Count of tags per location. Key=location, Value=count"
    )
