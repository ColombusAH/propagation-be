"""
Tests for app.utils.helpers module.
"""

from datetime import datetime
from app.utils.helpers import parse_tag_data, validate_epc, format_rssi


def test_parse_tag_data():
    """Test parsing raw tag data."""
    raw = {"epc": "E2001234", "rssi": -60.5, "antenna_port": 1, "extra": "ignore me"}

    parsed = parse_tag_data(raw)

    assert parsed["epc"] == "E2001234"
    assert parsed["rssi"] == -60.5
    assert parsed["antenna_port"] == 1
    assert "timestamp" in parsed
    # Should handle missing fields gracefully
    assert parsed["tid"] is None


def test_validate_epc_valid():
    """Test valid EPCs."""
    assert validate_epc("E2001234") is True
    assert validate_epc("ABCDEF0123456789") is True
    assert validate_epc("0000") is True


def test_validate_epc_invalid():
    """Test invalid EPCs."""
    assert validate_epc("") is False
    assert validate_epc(None) is False
    assert validate_epc("XYZ") is False  # Non-hex
    assert validate_epc("G200") is False


def test_format_rssi():
    """Test RSSI formatting/clamping."""
    assert format_rssi(-50.0) == -50.0
    assert format_rssi(-120.0) == -100.0  # Clamped min
    assert format_rssi(10.0) == 0.0  # Clamped max
    assert format_rssi(None) is None
