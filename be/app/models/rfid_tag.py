"""
SQLAlchemy models for RFID tag tracking system.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Index, Text
from sqlalchemy.sql import func
from app.services.database import Base


class RFIDTag(Base):
    """
    Master tag list - stores unique RFID tags with aggregated data.
    
    EPC is unique and indexed. On duplicate EPC scan, the existing record
    is updated (read_count incremented, last_seen updated).
    """
    __tablename__ = "rfid_tags"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    epc = Column(String(128), unique=True, nullable=False, index=True, comment="Electronic Product Code")
    tid = Column(String(128), nullable=True, index=True, comment="Tag ID")
    user_memory = Column(Text, nullable=True, comment="User-defined data (max 512 chars)")
    rssi = Column(Float, nullable=True, comment="Received Signal Strength Indicator (dBm)")
    antenna_port = Column(Integer, nullable=True, comment="Which antenna detected the tag")
    read_count = Column(Integer, default=1, nullable=False, comment="Number of times scanned")
    frequency = Column(Float, nullable=True, comment="Operating frequency in MHz")
    pc = Column(String(16), nullable=True, comment="Protocol Control bits")
    crc = Column(String(16), nullable=True, comment="Cyclic Redundancy Check")
    tag_metadata = Column(JSON, nullable=True, comment="Additional flexible data")
    location = Column(String(100), nullable=True, comment="Physical location where scanned")
    notes = Column(Text, nullable=True, comment="User notes (max 500 chars)")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Soft delete flag")
    first_seen = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="First scan timestamp")
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Most recent scan timestamp")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_rfid_tags_epc', 'epc'),
        Index('idx_rfid_tags_tid', 'tid'),
        Index('idx_rfid_tags_is_active', 'is_active'),
        Index('idx_rfid_tags_last_seen', 'last_seen'),
    )


class RFIDScanHistory(Base):
    """
    Complete audit trail - stores every single scan event.
    
    Every scan creates a new entry here, even if the tag already exists
    in rfid_tags. This provides a complete history of all scan events.
    """
    __tablename__ = "rfid_scan_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    epc = Column(String(128), nullable=False, index=True, comment="Tag EPC (no foreign key constraint)")
    tid = Column(String(128), nullable=True, comment="Tag ID")
    rssi = Column(Float, nullable=True, comment="Signal strength at scan time")
    antenna_port = Column(Integer, nullable=True, comment="Antenna that detected")
    frequency = Column(Float, nullable=True, comment="Frequency used")
    location = Column(String(100), nullable=True, comment="Location at scan time")
    reader_id = Column(String(100), nullable=True, comment="Identifier of the reader device")
    tag_metadata = Column(JSON, nullable=True, comment="Additional scan context")
    scanned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True, comment="Scan timestamp")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_rfid_scan_history_epc', 'epc'),
        Index('idx_rfid_scan_history_scanned_at', 'scanned_at'),
        Index('idx_rfid_scan_history_reader_id', 'reader_id'),
    )


