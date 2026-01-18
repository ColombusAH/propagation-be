"""
Comprehensive tests for helper utility functions.
Covers: parse_tag_data, validate_epc, format_rssi
"""

import pytest
from app.utils.helpers import parse_tag_data, validate_epc, format_rssi


class TestParseTagData:
    """Tests for parse_tag_data function."""

    def test_parse_complete_data(self):
        """Test parsing complete tag data."""
        raw = {
            "epc": "E280681000001234",
            "tid": "TID123",
            "rssi": -55.0,
            "antenna_port": 1,
            "frequency": 920.5,
            "pc": 3000,
            "crc": "1234",
            "metadata": {"type": "item"},
            "location": "Zone A"
        }
        
        result = parse_tag_data(raw)
        
        assert result["epc"] == "E280681000001234"
        assert result["tid"] == "TID123"
        assert result["rssi"] == -55.0
        assert result["antenna_port"] == 1
        assert result["frequency"] == 920.5
        assert result["pc"] == 3000
        assert result["crc"] == "1234"
        assert result["metadata"] == {"type": "item"}
        assert result["location"] == "Zone A"
        assert "timestamp" in result

    def test_parse_minimal_data(self):
        """Test parsing minimal tag data."""
        raw = {"epc": "E280681000001234"}
        
        result = parse_tag_data(raw)
        
        assert result["epc"] == "E280681000001234"
        assert result["tid"] is None
        assert result["rssi"] is None
        assert "timestamp" in result

    def test_parse_empty_data(self):
        """Test parsing empty tag data."""
        raw = {}
        
        result = parse_tag_data(raw)
        
        assert result["epc"] == ""
        assert "timestamp" in result


class TestValidateEpc:
    """Tests for validate_epc function."""

    def test_validate_valid_epc(self):
        """Test validating valid EPC."""
        assert validate_epc("E280681000001234") is True
        assert validate_epc("ABCDEF123456") is True
        assert validate_epc("0000000000") is True

    def test_validate_empty_epc(self):
        """Test validating empty EPC."""
        assert validate_epc("") is False
        assert validate_epc(None) is False

    def test_validate_invalid_epc_non_hex(self):
        """Test validating non-hex EPC."""
        assert validate_epc("GHIJKL123") is False
        assert validate_epc("Hello World") is False

    def test_validate_epc_max_length(self):
        """Test validating EPC at max length."""
        # 128 chars should be valid
        long_epc = "A" * 128
        assert validate_epc(long_epc) is True
        
        # Over 128 chars should be invalid
        too_long_epc = "A" * 129
        assert validate_epc(too_long_epc) is False


class TestFormatRssi:
    """Tests for format_rssi function."""

    def test_format_rssi_normal_range(self):
        """Test formatting RSSI in normal range."""
        assert format_rssi(-55.0) == -55.0
        assert format_rssi(-70.5) == -70.5

    def test_format_rssi_clamped_high(self):
        """Test formatting RSSI clamped to 0."""
        assert format_rssi(10.0) == 0
        assert format_rssi(5.5) == 0

    def test_format_rssi_clamped_low(self):
        """Test formatting RSSI clamped to -100."""
        assert format_rssi(-120.0) == -100
        assert format_rssi(-150.0) == -100

    def test_format_rssi_none(self):
        """Test formatting None RSSI."""
        assert format_rssi(None) is None

    def test_format_rssi_boundary_values(self):
        """Test formatting RSSI at boundary values."""
        assert format_rssi(0) == 0
        assert format_rssi(-100) == -100
