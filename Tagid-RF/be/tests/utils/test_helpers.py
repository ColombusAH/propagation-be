from datetime import datetime

import pytest

from app.utils.helpers import format_rssi, parse_tag_data, validate_epc


def test_parse_tag_data():
    raw = {"epc": "E2001", "rssi": -55.0, "location": "Warehouse"}
    parsed = parse_tag_data(raw)
    assert parsed["epc"] == "E2001"
    assert parsed["rssi"] == -55.0
    assert "timestamp" in parsed


def test_validate_epc_valid():
    assert validate_epc("E2001234") is True


def test_validate_epc_invalid():
    assert validate_epc("INVALID") is False
    assert validate_epc(None) is False


def test_format_rssi():
    assert format_rssi(-40) == -40
    assert format_rssi(-120) == -100
    assert format_rssi(10) == 0
    assert format_rssi(None) is None
