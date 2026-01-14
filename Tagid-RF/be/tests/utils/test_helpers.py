"""
Tests for utility helper functions.
Covers tag data parsing, EPC validation, and RSSI formatting.
"""
import pytest
from app.utils.helpers import parse_tag_data, validate_epc, format_rssi


# --- parse_tag_data Tests ---
def test_parse_tag_data_basic():
    """Test basic tag data parsing."""
    raw = {"epc": "E200001234ABCDEF", "rssi": -45, "antenna_port": 1}
    result = parse_tag_data(raw)

    assert result["epc"] == "E200001234ABCDEF"
    assert result["rssi"] == -45
    assert result["antenna_port"] == 1
    assert "timestamp" in result


def test_parse_tag_data_empty():
    """Test parsing empty tag data."""
    result = parse_tag_data({})

    assert result["epc"] == ""
    assert result["tid"] is None
    assert result["rssi"] is None


def test_parse_tag_data_full():
    """Test parsing full tag data with all fields."""
    raw = {
        "epc": "E200001234ABCDEF",
        "tid": "TID123",
        "rssi": -50,
        "antenna_port": 2,
        "frequency": 915.25,
        "pc": "3000",
        "crc": "ABCD",
        "metadata": {"key": "value"},
        "location": "Gate 1",
    }
    result = parse_tag_data(raw)

    assert result["epc"] == "E200001234ABCDEF"
    assert result["tid"] == "TID123"
    assert result["frequency"] == 915.25
    assert result["metadata"]["key"] == "value"
    assert result["location"] == "Gate 1"


# --- validate_epc Tests ---
def test_validate_epc_valid():
    """Test valid EPC validation."""
    assert validate_epc("E200001234ABCDEF") is True
    assert validate_epc("ABCDEF123456") is True
    assert validate_epc("1234567890ABCDEF") is True


def test_validate_epc_invalid_empty():
    """Test empty EPC is invalid."""
    assert validate_epc("") is False
    assert validate_epc(None) is False


def test_validate_epc_invalid_format():
    """Test non-hex EPC is invalid."""
    assert validate_epc("GHIJKL") is False  # Non-hex characters
    assert validate_epc("12345Z") is False


def test_validate_epc_too_long():
    """Test EPC too long (>128 chars) is invalid."""
    long_epc = "A" * 129
    assert validate_epc(long_epc) is False


def test_validate_epc_max_length():
    """Test EPC at max length (128 chars) is valid."""
    max_epc = "A" * 128
    assert validate_epc(max_epc) is True


# --- format_rssi Tests ---
def test_format_rssi_normal():
    """Test normal RSSI formatting."""
    assert format_rssi(-45) == -45
    assert format_rssi(-80) == -80


def test_format_rssi_none():
    """Test None RSSI returns None."""
    assert format_rssi(None) is None


def test_format_rssi_clamp_low():
    """Test RSSI below -100 is clamped."""
    assert format_rssi(-120) == -100


def test_format_rssi_clamp_high():
    """Test RSSI above 0 is clamped."""
    assert format_rssi(10) == 0
    assert format_rssi(5) == 0


def test_format_rssi_boundary():
    """Test RSSI at boundaries."""
    assert format_rssi(-100) == -100
    assert format_rssi(0) == 0
