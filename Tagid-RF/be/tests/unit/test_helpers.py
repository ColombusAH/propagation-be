"""
Unit tests for utility helper functions.
"""

import pytest
from datetime import datetime, timezone


@pytest.mark.unit
class TestParseTagData:
    """Tests for parse_tag_data function."""

    def test_parse_full_data(self):
        """Test parsing complete tag data."""
        from app.utils.helpers import parse_tag_data
        
        raw_data = {
            "epc": "E2001234567890AB",
            "tid": "TID123",
            "rssi": -45.5,
            "antenna_port": 1,
            "frequency": 920.5,
            "pc": "3000",
            "crc": "ABCD",
            "metadata": {"key": "value"},
            "location": "Store A"
        }
        
        result = parse_tag_data(raw_data)
        
        assert result["epc"] == "E2001234567890AB"
        assert result["tid"] == "TID123"
        assert result["rssi"] == -45.5
        assert result["antenna_port"] == 1
        assert result["location"] == "Store A"
        assert "timestamp" in result

    def test_parse_minimal_data(self):
        """Test parsing minimal tag data."""
        from app.utils.helpers import parse_tag_data
        
        raw_data = {"epc": "E200MINIMAL"}
        
        result = parse_tag_data(raw_data)
        
        assert result["epc"] == "E200MINIMAL"
        assert result["tid"] is None
        assert result["rssi"] is None

    def test_parse_empty_data(self):
        """Test parsing empty data."""
        from app.utils.helpers import parse_tag_data
        
        result = parse_tag_data({})
        
        assert result["epc"] == ""
        assert "timestamp" in result

    def test_parse_timestamp_is_current(self):
        """Test parsed timestamp is current."""
        from app.utils.helpers import parse_tag_data
        
        before = datetime.now(timezone.utc)
        result = parse_tag_data({"epc": "E200"})
        after = datetime.now(timezone.utc)
        
        # Timestamp should be ISO format
        assert "T" in result["timestamp"]


@pytest.mark.unit
class TestValidateEpc:
    """Tests for validate_epc function."""

    def test_valid_epc_hex(self):
        """Test valid hex EPC."""
        from app.utils.helpers import validate_epc
        
        assert validate_epc("E2001234567890AB") is True
        assert validate_epc("ABCDEF0123456789") is True
        assert validate_epc("0000000000000000") is True

    def test_valid_epc_lowercase(self):
        """Test valid lowercase hex EPC."""
        from app.utils.helpers import validate_epc
        
        assert validate_epc("e2001234567890ab") is True
        assert validate_epc("abcdef0123456789") is True

    def test_invalid_epc_empty(self):
        """Test empty EPC is invalid."""
        from app.utils.helpers import validate_epc
        
        assert validate_epc("") is False

    def test_invalid_epc_non_hex(self):
        """Test non-hex EPC is invalid."""
        from app.utils.helpers import validate_epc
        
        assert validate_epc("GHIJKLMNOP") is False
        assert validate_epc("not-hex-data") is False

    def test_invalid_epc_special_chars(self):
        """Test EPC with special characters is invalid."""
        from app.utils.helpers import validate_epc
        
        assert validate_epc("E200-1234-5678") is False
        assert validate_epc("E200 1234 5678") is False


@pytest.mark.unit
class TestFormatRssi:
    """Tests for format_rssi function."""

    def test_rssi_normal_range(self):
        """Test RSSI in normal range."""
        from app.utils.helpers import format_rssi
        
        assert format_rssi(-45.0) == -45.0
        assert format_rssi(-70.0) == -70.0
        assert format_rssi(-30.0) == -30.0

    def test_rssi_clamped_high(self):
        """Test RSSI clamped at 0."""
        from app.utils.helpers import format_rssi
        
        assert format_rssi(10.0) == 0
        assert format_rssi(0.0) == 0

    def test_rssi_clamped_low(self):
        """Test RSSI clamped at -100."""
        from app.utils.helpers import format_rssi
        
        assert format_rssi(-110.0) == -100
        assert format_rssi(-200.0) == -100

    def test_rssi_none(self):
        """Test RSSI handles None."""
        from app.utils.helpers import format_rssi
        
        assert format_rssi(None) is None

    def test_rssi_boundary_values(self):
        """Test RSSI boundary values."""
        from app.utils.helpers import format_rssi
        
        assert format_rssi(-100.0) == -100.0
        assert format_rssi(0.0) == 0.0
