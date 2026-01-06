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
class M200Commands:
    """M-200 Command Codes (2-byte values)"""

    # Module General Control Commands (Section 2.2)
    RFM_MODULE_INT = 0x0072  # Initialize device
    RFM_GET_DEVICE_INFO = 0x0070  # Get device info (Section 2.2.7) ⭐
    RFM_SET_PWR = 0x002F  # Set RF output power
    RFM_SET_GET_RFID_PRO = 0x0041  # Set/read RF protocol
    RFM_SET_GET_NETPARA = 0x0042  # Set/read network port info
    RFM_SET_GET_REMOTE_NETPARA = 0x0043  # Set/read remote network info
    RFM_SET_ALL_PARAM = 0x0051  # Set all parameters
    RFM_GET_ALL_PARAM = 0x0052  # Get all parameters
    RFM_SET_GET_IOPUT_PARAM = 0x0053  # Set/get I/O parameters
    RFM_SET_GET_WiFi_PARAM = 0x0044  # Set/get WiFi info
    RFM_SET_GET_PERMISSION_PARAM = 0x0054  # Set/get permission
    RFM_RELEASE_CLOSE_RELAY1 = 0x0055  # Release/close relay 1
    RFM_RELEASE_CLOSE_RELAY2 = 0x0056  # Release/close relay 2
    RFM_SET_GET_AntN_RSSI_Filter = 0x0057  # Set RSSI filter

    # ISO 18000-6C Protocol Commands (Section 2.3)
    RFM_INVENTORYISO_CONTINUE = 0x0001  # Tag inventory ⭐
    RFM_INVENTORY_STOP = 0x0028  # Stop inventory ⭐
    RFM_READISO_TAG = 0x002A  # Read tag data
    RFM_SETISO_SELECTMASK = 0x002D  # Select tag to operate
    RFM_SET_SELPRM = 0x005D  # Set Select command params
    RFM_GET_SELPRM = 0x005E  # Get Select command params
    RFM_SET_QUERY_PARAM = 0x005B  # Set Query command params
    RFM_GET_QUERY_PARAM = 0x005C  # Get Query command params

    # GPIO Control Commands (Section 2.4)
    RFM_SET_GET_GPIO_WORKPARAM = 0x0058  # Set/get GPIO params
    RFM_GET_GPIO_LEVELS = 0x0059  # Get GPIO levels

    # Gate Control Commands (Section 2.5)
    RFM_GET_GATE_STATUS = 0x005A  # Get gate status
    RFM_SET_GET_GATE_WORKPARAM = 0x005F  # Set/get gate params
    RFM_SET_GET_EAS_MASK = 0x0060  # Set/get EAS mask


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
