"""
Pydantic schemas for RFID tag validation and serialization.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class RFIDTagBase(BaseModel):
    """Base schema with common fields."""

    epc: str = Field(..., max_length=128, description="Electronic Product Code")
    tid: Optional[str] = Field(None, max_length=128, description="Tag ID")
    user_memory: Optional[str] = Field(None, description="User-defined data")
    rssi: Optional[float] = Field(None, description="Signal strength in dBm")
    antenna_port: Optional[int] = Field(None, ge=1, le=4, description="Antenna port (1-4)")
    frequency: Optional[float] = Field(None, description="Frequency in MHz")
    pc: Optional[str] = Field(None, max_length=16, description="Protocol Control bits")
    crc: Optional[str] = Field(None, max_length=16, description="Cyclic Redundancy Check")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    location: Optional[str] = Field(None, max_length=100, description="Physical location")
    notes: Optional[str] = Field(None, max_length=500, description="User notes")


class RFIDTagCreate(RFIDTagBase):
    """Schema for creating a new tag."""

    pass


class RFIDTagUpdate(BaseModel):
    """Schema for updating tag metadata."""

    location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    user_memory: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class RFIDTagResponse(RFIDTagBase):
    """Schema for tag response."""

    id: int
    read_count: int
    is_active: bool
    first_seen: datetime
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RFIDScanHistoryResponse(BaseModel):
    """Schema for scan history response."""

    id: int
    epc: str
    tid: Optional[str]
    rssi: Optional[float]
    antenna_port: Optional[int]
    frequency: Optional[float]
    location: Optional[str]
    reader_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
    scanned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RFIDTagStatsResponse(BaseModel):
    """Schema for statistics response."""

    total_tags: int
    active_tags: int
    scans_today: int
    scans_last_hour: int
    most_scanned_tag: Optional[Dict[str, Any]]
    average_rssi: Optional[float]
    tags_by_location: Dict[str, int]
