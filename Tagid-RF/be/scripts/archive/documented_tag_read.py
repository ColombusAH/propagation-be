"""
=============================================================================
RFID Tag Reader - Documented Debug Tool
=============================================================================

Purpose: Attempt to read an RFID tag with full traffic documentation.
         Every command and response is logged with hex values and explanations.

Protocol: Chafon M-200 Gate Reader (CF-M Gate Reader User Manual V1.2)

Frame Format:
    Command:  [HEAD][ADDR][CMD_H][CMD_L][LEN][DATA...][CRC_L][CRC_H]
    Response: [HEAD][ADDR][CMD_H][CMD_L][LEN][STATUS][DATA...][CRC_L][CRC_H]

Constants:
    HEAD = 0xCF (fixed header)
    ADDR = 0xFF (broadcast) or 0x00 (default device)

Usage:
    python documented_tag_read.py [IP_ADDRESS] [PORT]

    Default: 192.168.1.55:4001

Author: Generated for debugging RFID tag reading
Date: 2026-01-11
=============================================================================
"""

import socket
import struct
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ===========================================================================
# PROTOCOL CONSTANTS (from M-200 manual)
# ===========================================================================

HEAD = 0xCF  # Fixed header byte
BROADCAST_ADDR = 0xFF  # Broadcast address
DEFAULT_ADDR = 0x00  # Default device address

# CRC16 Constants (Appendix B)
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408

# Command Codes (Table A-7)
CMD_GET_DEVICE_INFO = 0x0070  # Get device info
CMD_INVENTORY_CONTINUE = 0x0001  # Tag inventory (continuous)
CMD_STOP_INVENTORY = 0x0028  # Stop inventory
CMD_SET_POWER = 0x002F  # Set RF power

# Status Codes (Appendix C - Table A-8)
STATUS_SUCCESS = 0x00
STATUS_INVENTORY_COMPLETE = 0x12  # No tags or inventory done
STATUS_TAG_TIMEOUT = 0x14

STATUS_DESCRIPTIONS = {
    0x00: "Success",
    0x01: "Parameter error",
    0x02: "Command failed (internal error)",
    0x12: "Inventory complete (no tags found)",
    0x14: "Tag response timeout",
    0x15: "Tag demodulation error",
    0xFF: "No more data",
}


# ===========================================================================
# LOGGING UTILITIES
# ===========================================================================


def log_header(title: str):
    """Print a section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def log_subheader(title: str):
    """Print a sub-section header."""
    print()
    print("+" + "-" * 68 + "+")
    print(f"| {title:<66} |")
    print("+" + "-" * 68 + "+")


def log_bytes(label: str, data: bytes, direction: str = ""):
    """Log bytes in hex format with nice formatting."""
    hex_str = data.hex().upper()
    # Split into groups of 2 for readability
    formatted_hex = " ".join(hex_str[i : i + 2] for i in range(0, len(hex_str), 2))

    arrow = "-->" if direction == "TX" else "<--" if direction == "RX" else "   "
    dir_label = f"[{direction}]" if direction else ""

    print(f"{arrow} {dir_label} {label}")
    print(f"   Hex ({len(data)} bytes): {formatted_hex}")


def log_frame_breakdown(data: bytes, is_response: bool = False):
    """Parse and explain each byte of a frame."""
    print()
    print("   Frame Breakdown:")
    print("   " + "-" * 65)

    if len(data) < 6:
        print(f"   [!] Frame too short ({len(data)} bytes, min 6 required)")
        return

    offset = 0

    # HEAD
    head = data[offset]
    print(
        f"   [0] HEAD    = 0x{head:02X} {'OK' if head == HEAD else 'ERROR Expected 0xCF'}"
    )
    offset += 1

    # ADDR
    addr = data[offset]
    addr_desc = "Broadcast" if addr == BROADCAST_ADDR else f"Device {addr}"
    print(f"   [1] ADDR    = 0x{addr:02X} ({addr_desc})")
    offset += 1

    # CMD (2 bytes, big-endian)
    cmd = struct.unpack(">H", data[offset : offset + 2])[0]
    cmd_names = {
        0x0070: "GET_DEVICE_INFO",
        0x0001: "INVENTORY_CONTINUE",
        0x0028: "STOP_INVENTORY",
        0x002F: "SET_POWER",
    }
    cmd_name = cmd_names.get(cmd, "UNKNOWN")
    print(f"   [2-3] CMD   = 0x{cmd:04X} ({cmd_name})")
    offset += 2

    # LEN
    data_len = data[offset]
    print(
        f"   [4] LEN     = 0x{data_len:02X} ({data_len} bytes of data {'+ STATUS' if is_response else ''})"
    )
    offset += 1

    if is_response and len(data) > offset:
        # STATUS
        status = data[offset]
        status_desc = STATUS_DESCRIPTIONS.get(status, "Unknown")
        print(f"   [5] STATUS  = 0x{status:02X} ({status_desc})")
        offset += 1

        # DATA (LEN - 1 bytes, since STATUS is included in LEN)
        actual_data_len = data_len - 1 if data_len > 0 else 0
        if actual_data_len > 0 and len(data) > offset:
            payload = data[offset : offset + actual_data_len]
            print(
                f"   [6-{5+actual_data_len}] DATA = {payload.hex().upper()} ({actual_data_len} bytes)"
            )
            offset += actual_data_len
    else:
        # Command DATA
        if data_len > 0 and len(data) > offset:
            payload = data[offset : offset + data_len]
            print(
                f"   [5-{4+data_len}] DATA = {payload.hex().upper()} ({data_len} bytes)"
            )
            offset += data_len

    # CRC (last 2 bytes)
    if len(data) >= offset + 2:
        crc = struct.unpack(">H", data[-2:])[0]
        # Verify CRC
        calculated_crc = calculate_crc16(data[:-2])
        crc_match = (
            "OK"
            if crc == calculated_crc
            else f"ERROR (calculated: 0x{calculated_crc:04X})"
        )
        print(f"   [{len(data)-2}-{len(data)-1}] CRC = 0x{crc:04X} {crc_match}")


# ===========================================================================
# CRC CALCULATION
# ===========================================================================


def calculate_crc16(data: bytes) -> int:
    """Calculate CRC16 checksum (M-200 manual Appendix B)."""
    crc_value = PRESET_VALUE

    for byte in data:
        crc_value ^= byte
        for _ in range(8):
            if crc_value & 0x0001:
                crc_value = (crc_value >> 1) ^ POLYNOMIAL
            else:
                crc_value = crc_value >> 1

    return crc_value


# ===========================================================================
# COMMAND BUILDING
# ===========================================================================


def build_command(cmd: int, data: bytes = b"", addr: int = BROADCAST_ADDR) -> bytes:
    """
    Build a command frame for M-200.

    Format: [HEAD][ADDR][CMD_H][CMD_L][LEN][DATA...][CRC_H][CRC_L]
    """
    # Frame without CRC
    frame = struct.pack(">BBHB", HEAD, addr, cmd, len(data)) + data

    # Calculate and append CRC (big-endian)
    crc = calculate_crc16(frame)
    frame += struct.pack(">H", crc)

    return frame


def build_get_device_info() -> bytes:
    """Build GET_DEVICE_INFO command (CMD 0x0070)."""
    return build_command(CMD_GET_DEVICE_INFO)


def build_inventory_command(inv_type: int = 0x00, inv_param: int = 1) -> bytes:
    """
    Build INVENTORY command (CMD 0x0001).

    Args:
        inv_type: 0x00 = by time (seconds), 0x01 = by cycle count
        inv_param: Duration in seconds or cycle count (1 = single cycle)
    """
    data = struct.pack("BB", inv_type, inv_param)
    return build_command(CMD_INVENTORY_CONTINUE, data)


def build_stop_inventory() -> bytes:
    """Build STOP_INVENTORY command (CMD 0x0028)."""
    return build_command(CMD_STOP_INVENTORY)


# ===========================================================================
# RESPONSE PARSING
# ===========================================================================


def parse_inventory_tags(data: bytes) -> List[Dict[str, Any]]:
    """
    Parse tag data from inventory response.

    Format per tag:
        [RSSI][ANT][PC_H][PC_L][EPC_LEN][EPC...]
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
            }
        )

        offset += 5 + epc_len

    return tags


# ===========================================================================
# MAIN READER LOGIC
# ===========================================================================


class DocumentedReader:
    """RFID Reader with full traffic documentation."""

    def __init__(self, ip: str, port: int, timeout: float = 5.0):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None

    def connect(self) -> bool:
        """Connect to the reader."""
        log_subheader("STEP 1: TCP Connection")
        print(f"   Target: {self.ip}:{self.port}")
        print(f"   Timeout: {self.timeout}s")

        try:
            print(f"\n   Creating TCP socket...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)

            print(f"   Connecting...")
            self.sock.connect((self.ip, self.port))

            print(f"   [OK] Connected successfully!")
            return True

        except socket.timeout:
            print(f"   [FAIL] Connection timeout ({self.timeout}s)")
            return False
        except ConnectionRefusedError:
            print(f"   [FAIL] Connection refused (is the reader on?)")
            return False
        except Exception as e:
            print(f"   [FAIL] Connection error: {e}")
            return False

    def send_and_receive(self, command_name: str, command: bytes) -> Optional[bytes]:
        """Send a command and receive the response with full logging."""
        if not self.sock:
            print("   [FAIL] Not connected!")
            return None

        log_subheader(f"COMMAND: {command_name}")

        # Log outgoing command
        log_bytes("Sending command", command, "TX")
        log_frame_breakdown(command, is_response=False)

        try:
            # Send
            print(f"\n   Transmitting {len(command)} bytes...")
            self.sock.sendall(command)
            print(f"   [OK] Sent successfully")

            # Receive
            print(f"\n   Waiting for response (timeout: {self.timeout}s)...")

            response = b""

            # Read header first (at least 6 bytes: HEAD + ADDR + CMD + LEN + STATUS)
            while len(response) < 6:
                chunk = self.sock.recv(1024)
                if not chunk:
                    print("   [FAIL] Connection closed by reader")
                    return None
                response += chunk

            # Parse LEN to know how much more to read
            data_len = response[4]
            expected_total = 5 + data_len + 2  # Header(5) + Data(LEN) + CRC(2)

            # Read remaining data
            while len(response) < expected_total:
                chunk = self.sock.recv(1024)
                if not chunk:
                    break
                response += chunk

            print(f"   [OK] Received {len(response)} bytes")

            # Log response
            print()
            log_bytes("Response received", response, "RX")
            log_frame_breakdown(response, is_response=True)

            return response

        except socket.timeout:
            print(f"   [FAIL] Response timeout ({self.timeout}s)")
            return None
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            return None

    def read_tags(self) -> List[Dict[str, Any]]:
        """Execute inventory and read tags."""
        # Build inventory command (1 second duration)
        cmd = build_inventory_command(inv_type=0x00, inv_param=1)

        response = self.send_and_receive("INVENTORY (0x0001)", cmd)

        if not response:
            return []

        # Parse response
        if len(response) < 8:
            print("\n   [!] Response too short to contain tags")
            return []

        status = response[5]

        if status == STATUS_INVENTORY_COMPLETE:
            print("\n   [INFO] No tags found (inventory complete)")
            return []

        if status != STATUS_SUCCESS:
            print(
                f"\n   [!] Status: {STATUS_DESCRIPTIONS.get(status, 'Unknown')} (0x{status:02X})"
            )
            return []

        # Parse tag data
        data_len = response[4] - 1  # Subtract STATUS byte
        if data_len <= 0:
            print("\n   [INFO] No tag data in response")
            return []

        tag_data = response[6 : 6 + data_len]
        tags = parse_inventory_tags(tag_data)

        if tags:
            log_subheader("TAGS FOUND")
            for i, tag in enumerate(tags, 1):
                print(f"   Tag #{i}:")
                print(f"      EPC: {tag['epc']}")
                print(f"      RSSI: {tag['rssi']} dBm")
                print(f"      Antenna: {tag['antenna_port']}")
                print(f"      PC: 0x{tag['pc']:04X}")

        return tags

    def get_device_info(self) -> Optional[bytes]:
        """Get device information."""
        cmd = build_get_device_info()
        return self.send_and_receive("GET_DEVICE_INFO (0x0070)", cmd)

    def disconnect(self):
        """Disconnect from reader."""
        log_subheader("DISCONNECTING")
        if self.sock:
            try:
                self.sock.close()
                print("   [OK] Socket closed")
            except Exception as e:
                print(f"   [!] Error closing socket: {e}")
            self.sock = None


# ===========================================================================
# MAIN
# ===========================================================================


def main():
    # Parse arguments
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.55"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 4001

    log_header("RFID TAG READER - DOCUMENTED DEBUG TOOL")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Target: {ip}:{port}")
    print(f"   Protocol: Chafon M-200 (binary)")

    reader = DocumentedReader(ip, port, timeout=5.0)

    try:
        # Step 1: Connect
        if not reader.connect():
            print("\n[FAIL] FAILED: Could not connect to reader")
            return 1

        # Step 2: Get device info (optional but useful)
        print("\n" + "-" * 70)
        print("   Querying device info...")
        reader.get_device_info()

        # Step 3: Read tags
        print("\n" + "-" * 70)
        print("   Scanning for RFID tags...")
        tags = reader.read_tags()

        # Summary
        log_header("SUMMARY")
        if tags:
            print(f"   [OK] Successfully read {len(tags)} tag(s)")
            for tag in tags:
                print(f"      * {tag['epc']} (RSSI: {tag['rssi']} dBm)")
        else:
            print("   [!] No tags read")
            print("   Tips:")
            print("   * Make sure a tag is within range")
            print("   * Check antenna connection")
            print("   * Verify RF power settings")

    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user")
    finally:
        reader.disconnect()

    return 0


if __name__ == "__main__":
    sys.exit(main())
