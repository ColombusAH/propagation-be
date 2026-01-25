"""
SQLAlchemy models for RFID tag tracking system.
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.sql import func

from app.services.database import Base


class RFIDTag(Base):
    __tablename__ = "rfid_tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    epc = Column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="Electronic Product Code",
    )
    tid = Column(String(128), nullable=True, index=True, comment="Tag ID")
    user_memory = Column(Text, nullable=True, comment="User-defined data (max 512 chars)")
    rssi = Column(Float, nullable=True, comment="Received Signal Strength Indicator (dBm)")
    antenna_port = Column(Integer, nullable=True, comment="Which antenna detected the tag")
    read_count = Column(Integer, default=1, nullable=False, comment="Number of times scanned")
    frequency = Column(Float, nullable=True, comment="Operating frequency in MHz")
    pc = Column(String(16), nullable=True, comment="Protocol Control bits")
    crc = Column(String(16), nullable=True, comment="Cyclic Redundancy Check")

    # FIX: rename attribute; keep DB column name "metadata"
    meta = Column("metadata", JSON, nullable=True, comment="Additional flexible data")

    location = Column(String(100), nullable=True, comment="Physical location where scanned")
    notes = Column(Text, nullable=True, comment="User notes (max 500 chars)")

    # NEW: Payment and product info for theft prevention
    is_paid = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Payment status - True if item has been paid for",
    )
    product_name = Column(String(255), nullable=True, comment="Product name for display")
    product_sku = Column(String(50), nullable=True, index=True, comment="Product SKU")
    price_cents = Column(Integer, nullable=True, comment="Price in cents/agorot")
    store_id = Column(Integer, nullable=True, index=True, comment="Store ID where tag belongs")
    paid_at = Column(DateTime(timezone=True), nullable=True, comment="When payment was made")

    is_active = Column(
        Boolean, default=True, nullable=False, index=True, comment="Soft delete flag"
    )
    first_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="First scan timestamp",
    )
    last_seen = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Most recent scan timestamp",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_rfid_tags_epc", "epc"),
        Index("idx_rfid_tags_tid", "tid"),
        Index("idx_rfid_tags_is_active", "is_active"),
        Index("idx_rfid_tags_last_seen", "last_seen"),
        Index("idx_rfid_tags_is_paid", "is_paid"),
        Index("idx_rfid_tags_store_id", "store_id"),
    )


class RFIDScanHistory(Base):
    __tablename__ = "rfid_scan_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    epc = Column(
        String(128),
        nullable=False,
        index=True,
        comment="Tag EPC (no foreign key constraint)",
    )
    tid = Column(String(128), nullable=True, comment="Tag ID")
    rssi = Column(Float, nullable=True, comment="Signal strength at scan time")
    antenna_port = Column(Integer, nullable=True, comment="Antenna that detected")
    frequency = Column(Float, nullable=True, comment="Frequency used")
    location = Column(String(100), nullable=True, comment="Location at scan time")
    reader_id = Column(String(100), nullable=True, comment="Identifier of the reader device")

    # FIX: rename attribute; keep DB column name "metadata"
    meta = Column("metadata", JSON, nullable=True, comment="Additional scan context")

    scanned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Scan timestamp",
    )

    __table_args__ = (
        Index("idx_rfid_scan_history_epc", "epc"),
        Index("idx_rfid_scan_history_scanned_at", "scanned_at"),
        Index("idx_rfid_scan_history_reader_id", "reader_id"),
    )


class RFIDReaderConfig(Base):
    """Stores configuration for RFID readers."""

    __tablename__ = "rfid_reader_configs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reader_id = Column(String(100), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # Supports IPv4 and IPv6
    port = Column(Integer, default=4001, nullable=False)
    power_dbm = Column(Integer, default=26, nullable=False)
    antenna_mask = Column(Integer, default=1, nullable=False)  # Bitmask (1=Ant1, 2=Ant2, 4=Ant3, 8=Ant4)
    rssi_filter = Column(Integer, default=0, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    meta = Column("metadata", JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
