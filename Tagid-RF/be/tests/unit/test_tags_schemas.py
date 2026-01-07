"""
Unit tests for Tags router schemas and validation.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError


@pytest.mark.unit
class TestRFIDTagSchemas:
    """Tests for RFID Tag Pydantic schemas."""

    def test_rfid_tag_create_schema(self):
        """Test RFIDTagCreate schema with valid data."""
        from app.schemas.rfid_tag import RFIDTagCreate
        
        tag = RFIDTagCreate(
            epc="E200-1234-5678-9ABC",
            tid="TID-001",
            rssi=-45.5,
            antenna_port=1,
            frequency=920.5,
            location="Store A"
        )
        
        assert tag.epc == "E200-1234-5678-9ABC"
        assert tag.rssi == -45.5
        assert tag.antenna_port == 1

    def test_rfid_tag_create_minimal(self):
        """Test RFIDTagCreate with only EPC."""
        from app.schemas.rfid_tag import RFIDTagCreate
        
        tag = RFIDTagCreate(epc="E200-MINIMAL")
        
        assert tag.epc == "E200-MINIMAL"
        assert tag.tid is None
        assert tag.rssi is None

    def test_rfid_tag_create_requires_epc(self):
        """Test RFIDTagCreate requires EPC field."""
        from app.schemas.rfid_tag import RFIDTagCreate
        
        with pytest.raises(ValidationError):
            RFIDTagCreate()

    def test_rfid_tag_update_schema(self):
        """Test RFIDTagUpdate schema."""
        from app.schemas.rfid_tag import RFIDTagUpdate
        
        update = RFIDTagUpdate(
            location="New Location",
            notes="Updated notes"
        )
        
        assert update.location == "New Location"
        assert update.notes == "Updated notes"
        assert update.is_active is None

    def test_rfid_tag_update_all_optional(self):
        """Test RFIDTagUpdate allows all optional fields."""
        from app.schemas.rfid_tag import RFIDTagUpdate
        
        # Should not raise - all fields are optional
        update = RFIDTagUpdate()
        assert update.location is None

    def test_rfid_tag_update_is_active(self):
        """Test RFIDTagUpdate is_active for soft delete."""
        from app.schemas.rfid_tag import RFIDTagUpdate
        
        update = RFIDTagUpdate(is_active=False)
        assert update.is_active is False

    def test_rfid_tag_response_schema(self):
        """Test RFIDTagResponse schema."""
        from app.schemas.rfid_tag import RFIDTagResponse
        
        now = datetime.now()
        response = RFIDTagResponse(
            id=1,
            epc="E200-TEST",
            tid="TID-001",
            user_memory=None,
            rssi=-45.0,
            antenna_port=1,
            read_count=10,
            frequency=920.5,
            pc=None,
            crc=None,
            metadata=None,
            location="Store",
            notes=None,
            is_active=True,
            first_seen=now,
            last_seen=now,
            created_at=now,
            updated_at=now
        )
        
        assert response.id == 1
        assert response.read_count == 10


@pytest.mark.unit
class TestRFIDScanHistorySchema:
    """Tests for RFID Scan History schema."""

    def test_scan_history_response(self):
        """Test RFIDScanHistoryResponse schema."""
        from app.schemas.rfid_tag import RFIDScanHistoryResponse
        
        now = datetime.now()
        history = RFIDScanHistoryResponse(
            id=1,
            epc="E200-TEST",
            tid="TID-001",
            rssi=-50.0,
            antenna_port=2,
            frequency=920.0,
            location="Exit Gate",
            reader_id="READER-001",
            metadata={"event": "exit"},
            scanned_at=now
        )
        
        assert history.reader_id == "READER-001"
        assert history.scanned_at == now


@pytest.mark.unit
class TestRFIDTagStatsSchema:
    """Tests for RFID Tag Stats schema."""

    def test_stats_response(self):
        """Test RFIDTagStatsResponse schema."""
        from app.schemas.rfid_tag import RFIDTagStatsResponse
        
        stats = RFIDTagStatsResponse(
            total_tags=100,
            active_tags=85,
            scans_today=356,
            scans_last_hour=42,
            most_scanned_tag={"id": 1, "epc": "E200-TEST", "read_count": 100},
            average_rssi=-52.3,
            tags_by_location={"Store A": 50, "Store B": 35}
        )
        
        assert stats.total_tags == 100
        assert stats.active_tags == 85
        assert stats.tags_by_location["Store A"] == 50


@pytest.mark.unit
class TestRFIDTagMetadata:
    """Tests for RFID Tag metadata handling."""

    def test_tag_with_metadata(self):
        """Test RFIDTagCreate with metadata."""
        from app.schemas.rfid_tag import RFIDTagCreate
        
        tag = RFIDTagCreate(
            epc="E200-META",
            metadata={"category": "clothing", "size": "XL", "color": "blue"}
        )
        
        assert tag.metadata["category"] == "clothing"
        assert tag.metadata["size"] == "XL"

    def test_tag_update_metadata(self):
        """Test RFIDTagUpdate metadata update."""
        from app.schemas.rfid_tag import RFIDTagUpdate
        
        update = RFIDTagUpdate(
            metadata={"status": "sold", "customer_id": "C123"}
        )
        
        assert update.metadata["status"] == "sold"


@pytest.mark.unit
class TestRSSIValidation:
    """Tests for RSSI value handling."""

    def test_rssi_typical_values(self):
        """Test typical RSSI values."""
        from app.schemas.rfid_tag import RFIDTagCreate
        
        # Close range
        tag_close = RFIDTagCreate(epc="E200-CLOSE", rssi=-25.0)
        assert tag_close.rssi == -25.0
        
        # Medium range
        tag_medium = RFIDTagCreate(epc="E200-MEDIUM", rssi=-50.0)
        assert tag_medium.rssi == -50.0
        
        # Far range
        tag_far = RFIDTagCreate(epc="E200-FAR", rssi=-80.0)
        assert tag_far.rssi == -80.0

    def test_rssi_null_allowed(self):
        """Test RSSI can be null."""
        from app.schemas.rfid_tag import RFIDTagCreate
        
        tag = RFIDTagCreate(epc="E200-NO-RSSI")
        assert tag.rssi is None


@pytest.mark.unit
class TestAntennaPort:
    """Tests for antenna port handling."""

    def test_antenna_port_values(self):
        """Test antenna port typical values."""
        from app.schemas.rfid_tag import RFIDTagCreate
        
        for port in [1, 2, 3, 4]:
            tag = RFIDTagCreate(epc=f"E200-PORT-{port}", antenna_port=port)
            assert tag.antenna_port == port


@pytest.mark.unit
class TestFrequency:
    """Tests for frequency handling."""

    def test_frequency_uhf_range(self):
        """Test UHF RFID frequency range."""
        from app.schemas.rfid_tag import RFIDTagCreate
        
        # US frequency range
        tag_us = RFIDTagCreate(epc="E200-US", frequency=915.0)
        assert tag_us.frequency == 915.0
        
        # EU frequency range
        tag_eu = RFIDTagCreate(epc="E200-EU", frequency=866.0)
        assert tag_eu.frequency == 866.0
