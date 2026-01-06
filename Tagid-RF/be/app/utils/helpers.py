"""
Utility functions for RFID tracking system.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def parse_tag_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse raw tag data from RFID reader into standardized format.

    Args:
        raw_data: Raw tag data from reader

    Returns:
        dict: Parsed tag data with standardized fields
    """
    return {
        "epc": raw_data.get("epc", ""),
        "tid": raw_data.get("tid"),
        "rssi": raw_data.get("rssi"),
        "antenna_port": raw_data.get("antenna_port"),
        "frequency": raw_data.get("frequency"),
        "pc": raw_data.get("pc"),
        "crc": raw_data.get("crc"),
        "metadata": raw_data.get("metadata"),
        "location": raw_data.get("location"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def validate_epc(epc: str) -> bool:
    """
    Validate EPC format.

    Args:
        epc: Electronic Product Code to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not epc:
        return False

    # EPC should be hexadecimal string
    try:
        int(epc, 16)
        return len(epc) <= 128
    except ValueError:
        return False


def format_rssi(rssi: Optional[float]) -> Optional[float]:
    """
    Format RSSI value (clamp to reasonable range).

    Args:
        rssi: Raw RSSI value in dBm

    Returns:
        float: Formatted RSSI value
    """
    if rssi is None:
        return None

    # RSSI typically ranges from -100 to 0 dBm
    return max(-100, min(0, rssi))
