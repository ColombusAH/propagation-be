"""
M-200 Gate Reader Protocol Implementation

Based on: CF-M Gate Reader User Manual V1.2
This module implements the M-Series specific protocol which is different
from standard Chafon CF-RU readers.

Frame Format (Table A-2 & A-3):
- Command:  [HEAD][ADDR][CMD_H][CMD_L][LEN][DATA...][CRC_L][CRC_H]
- Response: [HEAD][ADDR][CMD_H][CMD_L][LEN][STATUS][DATA...][CRC_L][CRC_H]
"""

import logging
import struct
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Frame constants
HEAD = 0xCF  # Fixed header byte from manual
BROADCAST_ADDR = 0xFF  # Broadcast address
DEFAULT_ADDR = 0x00  # Default device address

# CRC16 Constants (from Appendix B of manual)
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408


def calculate_crc16(data: bytes) -> int:
    """
    Calculate CRC16 checksum using algorithm from M-200 manual Appendix B.

    Args:
        data: Bytes to calculate checksum for

    Returns:
        16-bit CRC value
    """
    crc_value = PRESET_VALUE

    for byte in data:
        crc_value ^= byte
        for _ in range(8):
            if crc_value & 0x0001:
                crc_value = (crc_value >> 1) ^ POLYNOMIAL
            else:
                crc_value = crc_value >> 1

    return crc_value


@dataclass
class M200Response:
    """Parsed response from M-200 reader"""

    addr: int
    cmd: int
    status: int
    data: bytes
    crc: int

    @property
    def success(self) -> bool:
        """Check if command executed successfully (Appendix C)"""
        return self.status == 0x00


class M200Command:
    """
    M-200 Command Frame Builder

    Frame Format (from manual Table A-2):
    [HEAD][ADDR][CMD_H][CMD_L][LEN][DATA...][CRC_L][CRC_H]

    - HEAD: Fixed 0xCF (1 byte)
    - ADDR: Device address (1 byte, default 0x00, 0xFF for broadcast)
    - CMD: Command code (2 bytes, big-endian)
    - LEN: Data length (1 byte, 0-255)
    - DATA: Command data (variable)
    - CRC: CRC16 checksum (2 bytes, little-endian)
    """

    def __init__(self, cmd: int, data: bytes = b"", addr: int = DEFAULT_ADDR):
        """
        Initialize M-200 command.

        Args:
            cmd: Command code (2-byte value, see manual Section 2.1)
            data: Command data payload
            addr: Device address (default 0x00, use 0xFF for broadcast)
        """
        self.addr = addr
        self.cmd = cmd
        self.data = data

    def serialize(self) -> bytes:
        """
        Serialize command to bytes for transmission.

        Returns:
            Complete command frame with HEAD and CRC
        """
        # Build frame without CRC: [HEAD][ADDR][CMD_H][CMD_L][LEN][DATA]
        data_len = len(self.data)
        if data_len > 255:
            raise ValueError(f"Data too long: {data_len} bytes (max 255)")

        frame = struct.pack(">BBHB", HEAD, self.addr, self.cmd, data_len) + self.data

        # Calculate and append CRC (big-endian per manual: MSB first, LSB second)
        crc = calculate_crc16(frame)
        frame += struct.pack(">H", crc)

        return frame

    def __repr__(self) -> str:
        return f"M200Command(addr=0x{self.addr:02X}, cmd=0x{self.cmd:04X}, len={len(self.data)})"


class M200ResponseParser:
    """
    M-200 Response Frame Parser

    Response Format (from manual Table A-3):
    [HEAD][ADDR][CMD_H][CMD_L][LEN][STATUS][DATA...][CRC_L][CRC_H]
    """

    @staticmethod
    def parse(frame: bytes, strict_crc: bool = False) -> M200Response:
        """
        Parse response frame from M-200 reader.

        Args:
            frame: Raw response bytes
            strict_crc: If True, raise error on CRC mismatch. If False, log warning only.

        Returns:
            Parsed M200Response object

        Raises:
            ValueError: If frame is invalid or CRC check fails (when strict_crc=True)
        """
        if len(frame) < 8:  # Minimum: HEAD + ADDR + CMD(2) + LEN + STATUS + CRC(2)
            raise ValueError(f"Frame too short: {len(frame)} bytes (min 8)")

        # Parse header
        head = frame[0]
        if head != HEAD:
            raise ValueError(f"Invalid HEAD: 0x{head:02X} (expected 0x{HEAD:02X})")

        addr = frame[1]
        cmd = struct.unpack(">H", frame[2:4])[0]  # CMD is 2 bytes big-endian
        len_field = frame[4]  # LEN includes STATUS byte per manual Table A-3
        status = frame[5]

        # Per manual: LEN = length of Information Field (which includes STATUS + Data)
        # Frame = HEAD(1) + ADDR(1) + CMD(2) + LEN(1) + [LEN bytes] + CRC(2)
        # So: expected_len = 5 + len_field + 2 = 7 + len_field
        expected_len = 5 + len_field + 2
        if len(frame) != expected_len:
            raise ValueError(f"Invalid frame length: expected {expected_len}, got {len(frame)}")

        # Data starts after STATUS (byte 6) and is LEN-1 bytes (LEN includes STATUS)
        data_len = len_field - 1  # Subtract STATUS byte
        data = frame[6 : 6 + data_len]
        crc_received = struct.unpack(">H", frame[-2:])[0]

        # Verify CRC
        crc_calculated = calculate_crc16(frame[:-2])
        if crc_received != crc_calculated:
            error_msg = (
                f"CRC mismatch: received 0x{crc_received:04X}, calculated 0x{crc_calculated:04X}"
            )
            if strict_crc:
                raise ValueError(error_msg)
            else:
                logger.warning(
                    f"{error_msg} - Device may use proprietary CRC variant, continuing anyway"
                )

        return M200Response(addr=addr, cmd=cmd, status=status, data=data, crc=crc_received)


# Command Codes (from manual Section 2.1 - Table A-7)
# Command Codes (corrected for UHF Gate Reader V1.1)
class M200Commands:
    """M-200 / Gate Reader Command Codes (2-byte values)"""

    # ISO 18000-6C Protocol Commands
    RFM_READISO_TAG = 0x0003
    RFM_SETISO_SELECTMASK = 0x0007
    RFM_SET_SELPRM = 0x0010
    RFM_GET_SELPRM = 0x0011
    RFM_SET_QUERY_PARAM = 0x0012
    RFM_GET_QUERY_PARAM = 0x0013

    # Module Custom Directives
    RFM_MODULE_INT = 0x0050
    RFM_REBOOT = 0x0052  # Was confused with Get All Param!
    RFM_SET_PWR = 0x0053
    RFM_SET_GET_RFID_PRO = 0x0059
    RFM_SET_GET_NETPARA = 0x005F
    RFM_SET_GET_REMOTE_NETPARA = 0x0064
    RFM_GET_DEVICE_INFO = 0x0070
    RFM_SET_ALL_PARAM = 0x0071
    RFM_GET_ALL_PARAM = 0x0072
    RFM_SET_GET_IOPUT_PARAM = 0x0074
    RFM_SET_GET_WiFi_PARAM = 0x0075
    RFM_SET_GET_S_PERMISSION_PARAM = 0x0076
    RFM_RELEASE_CLOSE_RELAY1 = 0x0077
    RFM_RELEASE_CLOSE_RELAY2 = 0x0078
    RFM_SET_GET_AntN_RSSI_Filter = 0x0079

    # GPIO Control
    RFM_SET_GET_G_PIO_WORKPARAM = 0x0080
    RFM_GET_G_PIO_LEVEL = 0x0081

    # Gate Access Control
    RFM_GET_GATE_STATUS = 0x0082  # Also used for active tag reporting
    RFM_SET_GET_GATE_PARAM = 0x0083
    RFM_SET_GET_EAS_MASK = 0x0084

    # Legacy/Standard aliases (kept for compatibility logic if needed)
    RFM_INVENTORYISO_CONTINUE = 0x0001  # Standard Chafon inventory
    RFM_INVENTORY_STOP = 0x0028  # Standard Chafon stop


# Status Codes (from manual Appendix C - Table A-8)
class M200Status:
    """M-200 Status Codes"""

    SUCCESS = 0x00  # Command executed successfully
    PARAM_ERROR = 0x01  # Parameter value incorrect or out of range
    COMMAND_FAILED = 0x02  # Command execution failed (internal error)
    RESERVED = 0x03  # Reserved
    INVENTORY_COMPLETE = 0x12  # No inventory or inventory completed
    TAG_TIMEOUT = 0x14  # Tag response timeout
    TAG_DEMOD_ERROR = 0x15  # Demodulation tag response error
    AUTH_FAILED = 0x16  # Protocol authentication failed
    WRONG_PASSWORD = 0x17  # Wrong password
    NO_MORE_DATA = 0xFF  # No more data

    @staticmethod
    def get_description(status: int) -> str:
        """Get human-readable status description"""
        descriptions = {
            0x00: "Success",
            0x01: "Parameter error",
            0x02: "Command failed (internal error)",
            0x03: "Reserved",
            0x12: "Inventory complete (no tags found)",
            0x14: "Tag response timeout",
            0x15: "Tag demodulation error",
            0x16: "Authentication failed",
            0x17: "Wrong password",
            0xFF: "No more data",
        }
        return descriptions.get(status, f"Unknown status: 0x{status:02X}")


def parse_device_info(data: bytes) -> Dict[str, Any]:
    """
    Parse device info response (Section 2.2.7).

    Per manual, response format (total 152 bytes):
    - CPHardVer: 32 Bytes (CP hardware version string)
    - CPFirmVer: 32 Bytes (CP firmware version string)
    - CPSN_code: 12 Bytes (CP serial number)
    - RFIDModeVer: 32 Bytes (RFID module hardware version)
    - RFIDModeName: 32 Bytes (RFID module name)
    - RFIDMode_SNCode: 12 Bytes (RFID module serial number)
    """
    EXPECTED_LENGTH = 152  # 32 + 32 + 12 + 32 + 32 + 12

    if len(data) < EXPECTED_LENGTH:
        logger.warning(
            f"Device info response shorter than expected: {len(data)} bytes (expected {EXPECTED_LENGTH})"
        )
        # Try to parse what we have

    offset = 0

    # CPHardVer (32 bytes)
    cp_hw_ver = data[offset : offset + 32].rstrip(b"\x00").decode("ascii", errors="ignore").strip()
    offset += 32

    # CPFirmVer (32 bytes)
    cp_fw_ver = (
        data[offset : offset + 32].rstrip(b"\x00").decode("ascii", errors="ignore").strip()
        if len(data) >= offset + 32
        else ""
    )
    offset += 32

    # CPSN_code (12 bytes)
    cp_sn = (
        data[offset : offset + 12].rstrip(b"\x00").decode("ascii", errors="ignore").strip()
        if len(data) >= offset + 12
        else ""
    )
    offset += 12

    # RFIDModeVer (32 bytes)
    rfid_hw_ver = (
        data[offset : offset + 32].rstrip(b"\x00").decode("ascii", errors="ignore").strip()
        if len(data) >= offset + 32
        else ""
    )
    offset += 32

    # RFIDModeName (32 bytes)
    rfid_module_name = (
        data[offset : offset + 32].rstrip(b"\x00").decode("ascii", errors="ignore").strip()
        if len(data) >= offset + 32
        else ""
    )
    offset += 32

    # RFIDMode_SNCode (12 bytes)
    rfid_sn = (
        data[offset : offset + 12].rstrip(b"\x00").decode("ascii", errors="ignore").strip()
        if len(data) >= offset + 12
        else ""
    )

    return {
        "cp_hardware_version": cp_hw_ver,
        "cp_firmware_version": cp_fw_ver,
        "cp_serial_number": cp_sn,
        "rfid_hardware_version": rfid_hw_ver,
        "rfid_module_name": rfid_module_name,
        "rfid_serial_number": rfid_sn,
        "model": "M-200",
        "reader_type": "M-Series Gate Reader",
    }


def parse_inventory_response(data: bytes) -> List[Dict[str, Any]]:
    """
    Parse inventory response (Section 2.3.1).

    Response format for each tag:
    - RSSI (1 byte)
    - Ant (1 byte) - Antenna number
    - PC (2 bytes, big-endian)
    - EPC Length (1 byte)
    - EPC Data (variable)
    """
    tags = []
    offset = 0

    while offset < len(data):
        if offset + 5 > len(data):
            break

        rssi = data[offset]
        ant = data[offset + 1]
        pc = struct.unpack(">H", data[offset + 2 : offset + 4])[0]
        epc_len = data[offset + 4]

        if offset + 5 + epc_len > len(data):
            break

        epc = data[offset + 5 : offset + 5 + epc_len]

        tags.append(
            {
                "epc": epc.hex().upper(),
                "rssi": -rssi if rssi > 0 else rssi,  # Convert to negative dBm
                "antenna_port": ant,
                "pc": pc,
                "epc_length": epc_len,
            }
        )

        offset += 5 + epc_len

    return tags


# Helper functions to build common commands


def build_inventory_command(inv_type: int = 0x00, inv_param: int = 0) -> M200Command:
    """
    Build inventory command (Section 2.3.1).

    Args:
        inv_type: 0x00 = by time, 0x01 = by cycle count
        inv_param: Time in seconds (if type=0x00) or cycle count (if type=0x01)
                   0 = continuous until stop command

    Returns:
        M200Command for tag inventory
    """
    data = struct.pack("BB", inv_type, inv_param)
    return M200Command(M200Commands.RFM_INVENTORYISO_CONTINUE, data, addr=BROADCAST_ADDR)


def build_stop_inventory_command() -> M200Command:
    """Build stop inventory command (Section 2.3.2)"""
    return M200Command(M200Commands.RFM_INVENTORY_STOP, addr=BROADCAST_ADDR)


def build_get_device_info_command() -> M200Command:
    """
    Build get device info command (Section 2.2.7).

    Per manual: This command has NO data payload (LEN=0x00).

    Command format:
    - HEAD: 0xCF
    - ADDR: 0xFF (broadcast)
    - CMD: 0x0070
    - LEN: 0x00 (no data)
    - CRC: 2 bytes

    Returns:
        M200Command to get device information
    """
    return M200Command(M200Commands.RFM_GET_DEVICE_INFO, data=b"", addr=BROADCAST_ADDR)


def build_set_power_command(power_dbm: int) -> M200Command:
    """
    Build set RF power command (Section 2.2.3).

    Args:
        power_dbm: RF output power in dBm (typically 0-30)

    Returns:
        M200Command to set power
    """
    data = bytes([power_dbm])
    return M200Command(M200Commands.RFM_SET_PWR, data, addr=BROADCAST_ADDR)


def build_read_tag_command(mem_bank: int, start_addr: int, word_count: int) -> M200Command:
    """
    Build read tag data command (Section 2.3.3).

    Args:
        mem_bank: Memory bank (0=Reserved, 1=EPC, 2=TID, 3=User)
        start_addr: Starting address in words
        word_count: Number of words to read

    Returns:
        M200Command to read tag data
    """
    data = struct.pack("BBB", mem_bank, start_addr, word_count)
    return M200Command(M200Commands.RFM_READISO_TAG, data, addr=BROADCAST_ADDR)


def build_get_all_params_command() -> M200Command:
    """Build get all parameters command (Section 2.2.9)"""
    return M200Command(M200Commands.RFM_GET_ALL_PARAM, addr=BROADCAST_ADDR)


# =============================================================================
# HIGH PRIORITY - Module Control Commands
# =============================================================================


def build_module_init_command() -> M200Command:
    """
    Build module initialization command (Section 2.2.1).
    Resets the device to apply configuration changes.
    """
    return M200Command(M200Commands.RFM_MODULE_INT, addr=BROADCAST_ADDR)


def build_set_rf_protocol_command(protocol: int = 0x04) -> M200Command:
    """
    Build set RF protocol command (Section 2.2.4).

    Args:
        protocol: 0x04 = ISO18000-6C (EPC Gen2), default
    """
    data = struct.pack("BB", 0x01, protocol)  # 0x01 = Set mode
    return M200Command(M200Commands.RFM_SET_GET_RFID_PRO, data, addr=BROADCAST_ADDR)


def build_get_rf_protocol_command() -> M200Command:
    """Build get RF protocol command."""
    data = struct.pack("B", 0x02)  # 0x02 = Get mode
    return M200Command(M200Commands.RFM_SET_GET_RFID_PRO, data, addr=BROADCAST_ADDR)


# =============================================================================
# MEDIUM PRIORITY - Network & Configuration Commands
# =============================================================================


def build_set_network_command(
    ip: str, subnet: str = "255.255.255.0", gateway: str = "192.168.1.1", port: int = 4001
) -> M200Command:
    """
    Build set network parameters command (Section 2.2.5).

    Args:
        ip: Device IP address (e.g., "192.168.1.100")
        subnet: Subnet mask
        gateway: Gateway IP
        port: TCP port
    """
    ip_bytes = bytes(map(int, ip.split(".")))
    subnet_bytes = bytes(map(int, subnet.split(".")))
    gateway_bytes = bytes(map(int, gateway.split(".")))
    port_bytes = struct.pack(">H", port)

    data = struct.pack("B", 0x01) + ip_bytes + subnet_bytes + gateway_bytes + port_bytes
    return M200Command(M200Commands.RFM_SET_GET_NETPARA, data, addr=BROADCAST_ADDR)


def build_get_network_command() -> M200Command:
    """Build get network parameters command."""
    data = struct.pack("B", 0x02)  # 0x02 = Get mode
    return M200Command(M200Commands.RFM_SET_GET_NETPARA, data, addr=BROADCAST_ADDR)


def parse_network_response(data: bytes) -> Dict[str, Any]:
    """Parse network parameters response."""
    if len(data) < 14:
        return {"error": "Response too short"}

    return {
        "ip": f"{data[0]}.{data[1]}.{data[2]}.{data[3]}",
        "subnet": f"{data[4]}.{data[5]}.{data[6]}.{data[7]}",
        "gateway": f"{data[8]}.{data[9]}.{data[10]}.{data[11]}",
        "port": struct.unpack(">H", data[12:14])[0],
    }


def build_set_rssi_filter_command(antenna: int, rssi_threshold: int) -> M200Command:
    """
    Build RSSI filter command (Section 2.2.15).

    Args:
        antenna: Antenna number (1-4)
        rssi_threshold: Minimum RSSI value (0-255, typically 30-80)
    """
    data = struct.pack("BBB", 0x01, antenna, rssi_threshold)  # 0x01 = Set
    return M200Command(M200Commands.RFM_SET_GET_AntN_RSSI_Filter, data, addr=BROADCAST_ADDR)


def build_get_rssi_filter_command(antenna: int) -> M200Command:
    """Build get RSSI filter command."""
    data = struct.pack("BB", 0x02, antenna)  # 0x02 = Get
    return M200Command(M200Commands.RFM_SET_GET_AntN_RSSI_Filter, data, addr=BROADCAST_ADDR)


def build_set_all_params_command(config: Dict[str, Any]) -> M200Command:
    """
    Build set all parameters command (Section 2.2.8).

    Args:
        config: Dictionary with configuration values
    """
    # Build config bytes based on manual structure
    power = config.get("power", 26)
    antenna = config.get("antenna", 0x0F)  # All antennas

    data = struct.pack("BB", power, antenna)
    # Add more config bytes as needed

    return M200Command(M200Commands.RFM_SET_ALL_PARAM, data, addr=BROADCAST_ADDR)


# =============================================================================
# ISO 18000-6C Tag Commands
# =============================================================================


def build_select_tag_command(
    epc_mask: str, mask_length: int = None, target: int = 0x00, action: int = 0x00
) -> M200Command:
    """
    Build select tag command (Section 2.3.4).
    Used to target specific tag(s) for subsequent operations.

    Args:
        epc_mask: Hex string of EPC to match
        mask_length: Number of bits to match (default: full EPC)
        target: Target flag (0x00 = S0)
        action: Action (0x00 = match->A, not match->B)
    """
    mask_bytes = bytes.fromhex(epc_mask)
    if mask_length is None:
        mask_length = len(mask_bytes) * 8

    data = struct.pack("BBB", target, action, mask_length) + mask_bytes
    return M200Command(M200Commands.RFM_SETISO_SELECTMASK, data, addr=BROADCAST_ADDR)


def build_set_query_param_command(
    q_value: int = 4, session: int = 0, target: int = 0
) -> M200Command:
    """
    Build set Query parameters command (Section 2.3.7).

    Args:
        q_value: Q value (0-15), affects number of slots
        session: Session (0-3)
        target: Target (0=A, 1=B)
    """
    data = struct.pack("BBB", q_value, session, target)
    return M200Command(M200Commands.RFM_SET_QUERY_PARAM, data, addr=BROADCAST_ADDR)


def build_get_query_param_command() -> M200Command:
    """Build get Query parameters command."""
    return M200Command(M200Commands.RFM_GET_QUERY_PARAM, addr=BROADCAST_ADDR)


def build_set_select_param_command(select_flag: int = 0x00, truncate: int = 0x00) -> M200Command:
    """Build set Select parameters command (Section 2.3.5)."""
    data = struct.pack("BB", select_flag, truncate)
    return M200Command(M200Commands.RFM_SET_SELPRM, data, addr=BROADCAST_ADDR)


def build_get_select_param_command() -> M200Command:
    """Build get Select parameters command."""
    return M200Command(M200Commands.RFM_GET_SELPRM, addr=BROADCAST_ADDR)


# =============================================================================
# GPIO Control Commands
# =============================================================================


def build_set_gpio_param_command(
    pin: int, direction: int, level: int = 0x00  # 0x00 = Input, 0x01 = Output
) -> M200Command:
    """
    Build GPIO configuration command (Section 2.4.1).

    Args:
        pin: GPIO pin number (1-4)
        direction: 0x00 = Input, 0x01 = Output
        level: Initial output level (0x00 = Low, 0x01 = High)
    """
    data = struct.pack("BBBB", 0x01, pin, direction, level)  # 0x01 = Set
    return M200Command(M200Commands.RFM_SET_GET_GPIO_WORKPARAM, data, addr=BROADCAST_ADDR)


def build_get_gpio_param_command(pin: int) -> M200Command:
    """Build get GPIO parameters command."""
    data = struct.pack("BB", 0x02, pin)  # 0x02 = Get
    return M200Command(M200Commands.RFM_SET_GET_GPIO_WORKPARAM, data, addr=BROADCAST_ADDR)


def build_get_gpio_levels_command() -> M200Command:
    """Build get GPIO levels command (Section 2.4.2)."""
    return M200Command(M200Commands.RFM_GET_GPIO_LEVELS, addr=BROADCAST_ADDR)


def parse_gpio_levels(data: bytes) -> Dict[str, int]:
    """Parse GPIO levels response."""
    if len(data) < 4:
        return {}
    return {
        "gpio1": data[0],
        "gpio2": data[1],
        "gpio3": data[2],
        "gpio4": data[3],
    }


# =============================================================================
# Relay Control Commands
# =============================================================================


def build_relay1_command(close: bool = True) -> M200Command:
    """
    Build relay 1 control command (Section 2.2.13).

    Args:
        close: True = close relay, False = open relay
    """
    data = struct.pack("B", 0x01 if close else 0x00)
    return M200Command(M200Commands.RFM_RELEASE_CLOSE_RELAY1, data, addr=BROADCAST_ADDR)


def build_relay2_command(close: bool = True) -> M200Command:
    """
    Build relay 2 control command (Section 2.2.14).

    Args:
        close: True = close relay, False = open relay
    """
    data = struct.pack("B", 0x01 if close else 0x00)
    return M200Command(M200Commands.RFM_RELEASE_CLOSE_RELAY2, data, addr=BROADCAST_ADDR)


# =============================================================================
# Gate Control Commands
# =============================================================================


def build_get_gate_status_command() -> M200Command:
    """Build get gate status command (Section 2.5.1)."""
    return M200Command(M200Commands.RFM_GET_GATE_STATUS, addr=BROADCAST_ADDR)


def parse_gate_status(data: bytes) -> Dict[str, Any]:
    """Parse gate status response."""
    if len(data) < 2:
        return {"error": "Response too short"}

    return {
        "mode": data[0],  # 0x00 = idle, 0x01 = detecting
        "direction": data[1] if len(data) > 1 else None,  # 0x01 = entry, 0x02 = exit
    }


def build_set_gate_param_command(
    mode: int = 0x01, sensitivity: int = 0x50, direction_detect: bool = True
) -> M200Command:
    """
    Build set gate parameters command (Section 2.5.2).

    Args:
        mode: 0x00 = disabled, 0x01 = enabled
        sensitivity: Detection sensitivity (0-255)
        direction_detect: Enable direction detection
    """
    data = struct.pack("BBB", 0x01, mode, sensitivity)  # 0x01 = Set
    data += struct.pack("B", 0x01 if direction_detect else 0x00)
    return M200Command(M200Commands.RFM_SET_GET_GATE_WORKPARAM, data, addr=BROADCAST_ADDR)


def build_get_gate_param_command() -> M200Command:
    """Build get gate parameters command."""
    data = struct.pack("B", 0x02)  # 0x02 = Get
    return M200Command(M200Commands.RFM_SET_GET_GATE_WORKPARAM, data, addr=BROADCAST_ADDR)


def build_set_eas_mask_command(eas_data: bytes) -> M200Command:
    """
    Build set EAS mask command (Section 2.5.3).

    Args:
        eas_data: EAS matching data bytes
    """
    data = struct.pack("B", 0x01) + eas_data  # 0x01 = Set
    return M200Command(M200Commands.RFM_SET_GET_EAS_MASK, data, addr=BROADCAST_ADDR)


def build_get_eas_mask_command() -> M200Command:
    """Build get EAS mask command."""
    data = struct.pack("B", 0x02)  # 0x02 = Get
    return M200Command(M200Commands.RFM_SET_GET_EAS_MASK, data, addr=BROADCAST_ADDR)


# =============================================================================
# Remote Network & WiFi Commands
# =============================================================================


def build_set_remote_server_command(ip: str, port: int = 4001, enable: bool = True) -> M200Command:
    """
    Build set remote server command (Section 2.2.6).
    Device will forward tag data to this server.

    Args:
        ip: Remote server IP
        port: Remote server port
        enable: Enable/disable forwarding
    """
    ip_bytes = bytes(map(int, ip.split(".")))
    data = struct.pack("B", 0x01)  # 0x01 = Set
    data += ip_bytes
    data += struct.pack(">H", port)
    data += struct.pack("B", 0x01 if enable else 0x00)
    return M200Command(M200Commands.RFM_SET_GET_REMOTE_NETPARA, data, addr=BROADCAST_ADDR)


def build_get_remote_server_command() -> M200Command:
    """Build get remote server command."""
    data = struct.pack("B", 0x02)
    return M200Command(M200Commands.RFM_SET_GET_REMOTE_NETPARA, data, addr=BROADCAST_ADDR)


def build_set_wifi_command(ssid: str, password: str, security: int = 0x03) -> M200Command:  # WPA2
    """
    Build set WiFi parameters command (Section 2.2.10).

    Args:
        ssid: WiFi network name (max 32 chars)
        password: WiFi password (max 32 chars)
        security: 0x00=Open, 0x01=WEP, 0x02=WPA, 0x03=WPA2
    """
    ssid_bytes = ssid.encode("utf-8")[:32].ljust(32, b"\x00")
    pass_bytes = password.encode("utf-8")[:32].ljust(32, b"\x00")

    data = struct.pack("B", 0x01) + ssid_bytes + pass_bytes + struct.pack("B", security)
    return M200Command(M200Commands.RFM_SET_GET_WiFi_PARAM, data, addr=BROADCAST_ADDR)


def build_get_wifi_command() -> M200Command:
    """Build get WiFi parameters command."""
    data = struct.pack("B", 0x02)
    return M200Command(M200Commands.RFM_SET_GET_WiFi_PARAM, data, addr=BROADCAST_ADDR)


# =============================================================================
# I/O and Permission Commands
# =============================================================================


def build_set_io_param_command(config: Dict[str, int]) -> M200Command:
    """Build set I/O parameters command (Section 2.2.11)."""
    # Pack I/O configuration
    trigger_mode = config.get("trigger_mode", 0x00)
    output_mode = config.get("output_mode", 0x00)

    data = struct.pack("BBB", 0x01, trigger_mode, output_mode)
    return M200Command(M200Commands.RFM_SET_GET_IOPUT_PARAM, data, addr=BROADCAST_ADDR)


def build_get_io_param_command() -> M200Command:
    """Build get I/O parameters command."""
    data = struct.pack("B", 0x02)
    return M200Command(M200Commands.RFM_SET_GET_IOPUT_PARAM, data, addr=BROADCAST_ADDR)


def build_set_permission_command(password: str = "") -> M200Command:
    """Build set permission/password command (Section 2.2.12)."""
    pass_bytes = password.encode("utf-8")[:8].ljust(8, b"\x00")
    data = struct.pack("B", 0x01) + pass_bytes
    return M200Command(M200Commands.RFM_SET_GET_PERMISSION_PARAM, data, addr=BROADCAST_ADDR)


def build_get_permission_command() -> M200Command:
    """Build get permission status command."""
    data = struct.pack("B", 0x02)
    return M200Command(M200Commands.RFM_SET_GET_PERMISSION_PARAM, data, addr=BROADCAST_ADDR)
