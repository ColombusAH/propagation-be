"""
Unit tests for RFID Tag model.
"""

import pytest
from datetime import datetime, timezone


@pytest.mark.unit
class TestRFIDTagModel:
    """Tests for RFIDTag model."""

    def test_rfid_tag_creation_basic(self):
        """Test basic RFIDTag creation."""
        from app.models.rfid_tag import RFIDTag
        
        tag = RFIDTag(epc="E200-1234-5678-9ABC")
        
        assert tag.epc == "E200-1234-5678-9ABC"
        # is_paid has default=False in column definition
        is_paid_col = RFIDTag.__table__.c.is_paid
        assert is_paid_col.default.arg is False

    def test_rfid_tag_full_creation(self):
        """Test RFIDTag with all fields."""
        from app.models.rfid_tag import RFIDTag
        
        tag = RFIDTag(
            epc="E200-1234-5678-9ABC",
            tid="TID-001",
            user_memory="Custom data",
            rssi=-45.5,
            antenna_port=1,
            read_count=10,
            frequency=920.5,
            pc="3000",
            crc="ABCD",
            location="Store 1",
            notes="Test tag",
            is_paid=True,
            product_name="Blue Jeans",
            product_sku="JEANS-BLU-32",
            price_cents=12900,
            store_id=1
        )
        
        assert tag.epc == "E200-1234-5678-9ABC"
        assert tag.tid == "TID-001"
        assert tag.rssi == -45.5
        assert tag.antenna_port == 1
        assert tag.read_count == 10
        assert tag.frequency == 920.5
        assert tag.location == "Store 1"
        assert tag.is_paid is True
        assert tag.product_name == "Blue Jeans"
        assert tag.price_cents == 12900

    def test_rfid_tag_metadata_field(self):
        """Test RFIDTag meta (metadata) field."""
        from app.models.rfid_tag import RFIDTag
        
        tag = RFIDTag(
            epc="E200-META-TEST",
            meta={"category": "clothing", "size": "M"}
        )
        
        assert tag.meta == {"category": "clothing", "size": "M"}


@pytest.mark.unit
class TestRFIDScanHistoryModel:
    """Tests for RFIDScanHistory model."""

    def test_scan_history_creation(self):
        """Test RFIDScanHistory creation."""
        from app.models.rfid_tag import RFIDScanHistory
        
        scan = RFIDScanHistory(
            epc="E200-1234-5678-9ABC",
            tid="TID-001",
            rssi=-50.0,
            antenna_port=2,
            frequency=920.0,
            location="Exit Gate",
            reader_id="READER-001"
        )
        
        assert scan.epc == "E200-1234-5678-9ABC"
        assert scan.reader_id == "READER-001"
        assert scan.location == "Exit Gate"

    def test_scan_history_metadata(self):
        """Test RFIDScanHistory meta field."""
        from app.models.rfid_tag import RFIDScanHistory
        
        scan = RFIDScanHistory(
            epc="E200-SCAN-TEST",
            meta={"event": "exit", "gate": "main"}
        )
        
        assert scan.meta == {"event": "exit", "gate": "main"}


@pytest.mark.unit
class TestRFIDTagIndexes:
    """Tests for RFID table indexes configuration."""

    def test_rfid_tag_has_required_indexes(self):
        """Test RFIDTag table has required indexes."""
        from app.models.rfid_tag import RFIDTag
        
        # Check __table_args__ contains expected indexes
        table_args = RFIDTag.__table_args__
        
        index_names = [idx.name for idx in table_args if hasattr(idx, 'name')]
        
        assert "idx_rfid_tags_epc" in index_names
        assert "idx_rfid_tags_tid" in index_names
        assert "idx_rfid_tags_is_active" in index_names
        assert "idx_rfid_tags_is_paid" in index_names
        assert "idx_rfid_tags_store_id" in index_names

    def test_scan_history_has_required_indexes(self):
        """Test RFIDScanHistory table has required indexes."""
        from app.models.rfid_tag import RFIDScanHistory
        
        table_args = RFIDScanHistory.__table_args__
        
        index_names = [idx.name for idx in table_args if hasattr(idx, 'name')]
        
        assert "idx_rfid_scan_history_epc" in index_names
        assert "idx_rfid_scan_history_scanned_at" in index_names
        assert "idx_rfid_scan_history_reader_id" in index_names
