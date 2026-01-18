"""
=============================================================================
M-200 Protocol - Test ALL Commands
=============================================================================
Tests every command from the M-200 manual and reports which ones work.
Based on: app/services/m200_protocol.py
=============================================================================
"""

import socket
import struct
import sys
import time
from datetime import datetime

# Protocol constants
HEAD = 0xCF
BROADCAST_ADDR = 0xFF
DEFAULT_ADDR = 0x00
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408

# All commands from M-200 manual (Section 2.1 - Table A-7)
ALL_COMMANDS = {
    # Module General Control Commands (Section 2.2)
    0x0072: ("RFM_MODULE_INT", "Initialize device", b""),
    0x0070: ("RFM_GET_DEVICE_INFO", "Get device info", b""),
    0x002F: ("RFM_SET_PWR", "Set RF power (30dBm)", bytes([30])),
    0x0041: ("RFM_SET_GET_RFID_PRO", "Get RF protocol", bytes([0x00])),  # 0x00 = read
    0x0042: ("RFM_SET_GET_NETPARA", "Get network params", bytes([0x00])),
    0x0043: ("RFM_SET_GET_REMOTE_NETPARA", "Get remote network", bytes([0x00])),
    0x0052: ("RFM_GET_ALL_PARAM", "Get all parameters", b""),
    0x0053: ("RFM_SET_GET_IOPUT_PARAM", "Get I/O params", bytes([0x00])),
    0x0044: ("RFM_SET_GET_WiFi_PARAM", "Get WiFi info", bytes([0x00])),
    0x0054: ("RFM_SET_GET_PERMISSION_PARAM", "Get permission", bytes([0x00])),
    0x0055: ("RFM_RELEASE_CLOSE_RELAY1", "Toggle relay 1", bytes([0x00])),
    0x0056: ("RFM_RELEASE_CLOSE_RELAY2", "Toggle relay 2", bytes([0x00])),
    0x0057: ("RFM_SET_GET_AntN_RSSI_Filter", "Get RSSI filter", bytes([0x00])),
    # ISO 18000-6C Protocol Commands (Section 2.3)
    0x0001: ("RFM_INVENTORYISO_CONTINUE", "Tag inventory (1 sec)", bytes([0x00, 0x01])),
    0x0028: ("RFM_INVENTORY_STOP", "Stop inventory", b""),
    0x002A: (
        "RFM_READISO_TAG",
        "Read tag (TID bank)",
        bytes([0x02, 0x00, 0x06]),
    ),  # Bank 2, addr 0, 6 words
    0x002D: ("RFM_SETISO_SELECTMASK", "Set select mask", b""),
    0x005D: ("RFM_SET_SELPRM", "Set Select params", b""),
    0x005E: ("RFM_GET_SELPRM", "Get Select params", b""),
    0x005B: ("RFM_SET_QUERY_PARAM", "Set Query params", b""),
    0x005C: ("RFM_GET_QUERY_PARAM", "Get Query params", b""),
    # GPIO Control Commands (Section 2.4)
    0x0058: ("RFM_SET_GET_GPIO_WORKPARAM", "Get GPIO params", bytes([0x00])),
    0x0059: ("RFM_GET_GPIO_LEVELS", "Get GPIO levels", b""),
    # Gate Control Commands (Section 2.5)
    0x005A: ("RFM_GET_GATE_STATUS", "Get gate status", b""),
    0x005F: ("RFM_SET_GET_GATE_WORKPARAM", "Get gate params", bytes([0x00])),
    0x0060: ("RFM_SET_GET_EAS_MASK", "Get EAS mask", bytes([0x00])),
}

# Status descriptions
STATUS_DESC = {
    0x00: "Success",
    0x01: "Parameter error",
    0x02: "Command failed",
    0x03: "Reserved",
    0x12: "Inventory complete (no tags)",
    0x14: "Tag timeout",
    0x15: "Demodulation error",
    0x16: "Auth failed",
    0x17: "Wrong password",
    0xFF: "No more data",
}


def calculate_crc16(data):
    crc = PRESET_VALUE
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ POLYNOMIAL if crc & 0x0001 else crc >> 1
    return crc


def build_command(cmd, data=b"", addr=BROADCAST_ADDR):
    frame = struct.pack(">BBHB", HEAD, addr, cmd, len(data)) + data
    crc = calculate_crc16(frame)
    frame += struct.pack(">H", crc)
    return frame


def hex_str(data):
    return " ".join(f"{b:02X}" for b in data)


def test_command(sock, cmd_code, cmd_name, description, data, timeout=3.0):
    """Test a single command and return result."""
    cmd = build_command(cmd_code, data)

    result = {
        "cmd": cmd_code,
        "name": cmd_name,
        "desc": description,
        "tx": hex_str(cmd),
        "rx": None,
        "status": None,
        "status_desc": None,
        "success": False,
        "error": None,
    }

    try:
        # Clear any buffered data first
        sock.setblocking(False)
        try:
            sock.recv(4096)
        except:
            pass
        sock.setblocking(True)
        sock.settimeout(timeout)

        # Send command
        sock.sendall(cmd)

        # Receive response
        response = sock.recv(1024)
        result["rx"] = hex_str(response)

        # Parse response
        if len(response) >= 6 and response[0] == HEAD:
            resp_cmd = struct.unpack(">H", response[2:4])[0]
            resp_len = response[4]
            resp_status = response[5]

            result["status"] = resp_status
            result["status_desc"] = STATUS_DESC.get(resp_status, f"Unknown (0x{resp_status:02X})")

            # Check if successful
            if resp_status == 0x00:
                result["success"] = True
            elif resp_status == 0x12:  # Inventory complete (no tags) is also "working"
                result["success"] = True
                result["status_desc"] = "No tags found"
        else:
            result["error"] = "Invalid response format"

    except socket.timeout:
        result["error"] = "TIMEOUT"
    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022

    print("=" * 70)
    print("M-200 PROTOCOL - COMPLETE COMMAND TEST")
    print("=" * 70)
    print(f"Target: {ip}:{port}")
    print(f"Time: {datetime.now()}")
    print(f"Testing {len(ALL_COMMANDS)} commands...")
    print()

    # Connect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((ip, port))
        print(f"[OK] Connected to {ip}:{port}")
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        return 1

    print()
    print("-" * 70)

    results = []
    working = []
    not_working = []

    for cmd_code, (cmd_name, description, data) in ALL_COMMANDS.items():
        print(f"\nTesting: 0x{cmd_code:04X} - {cmd_name}")
        print(f"  Desc: {description}")

        result = test_command(sock, cmd_code, cmd_name, description, data)
        results.append(result)

        print(f"  TX: {result['tx']}")
        if result["rx"]:
            print(f"  RX: {result['rx']}")

        if result["error"]:
            print(f"  Result: [FAIL] {result['error']}")
            not_working.append(result)
        elif result["success"]:
            print(f"  Result: [OK] {result['status_desc']}")
            working.append(result)
        else:
            print(f"  Result: [FAIL] Status: {result['status_desc']}")
            not_working.append(result)

        time.sleep(0.3)  # Small delay between commands

    sock.close()

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    print(f"WORKING COMMANDS ({len(working)}/{len(ALL_COMMANDS)}):")
    print("-" * 40)
    for r in working:
        print(f"  [OK] 0x{r['cmd']:04X} - {r['name']}")

    print()
    print(f"NOT WORKING ({len(not_working)}/{len(ALL_COMMANDS)}):")
    print("-" * 40)
    for r in not_working:
        reason = r["error"] if r["error"] else r["status_desc"]
        print(f"  [X] 0x{r['cmd']:04X} - {r['name']} ({reason})")

    # Save detailed results to file
    with open("command_test_results.txt", "w", encoding="utf-8") as f:
        f.write(f"M-200 Command Test Results - {datetime.now()}\n")
        f.write(f"Target: {ip}:{port}\n")
        f.write("=" * 70 + "\n\n")

        f.write("WORKING COMMANDS:\n")
        f.write("-" * 40 + "\n")
        for r in working:
            f.write(f"0x{r['cmd']:04X} - {r['name']}\n")
            f.write(f"  TX: {r['tx']}\n")
            f.write(f"  RX: {r['rx']}\n")
            f.write(f"  Status: {r['status_desc']}\n\n")

        f.write("\nNOT WORKING:\n")
        f.write("-" * 40 + "\n")
        for r in not_working:
            f.write(f"0x{r['cmd']:04X} - {r['name']}\n")
            f.write(f"  TX: {r['tx']}\n")
            f.write(f"  RX: {r['rx']}\n")
            f.write(f"  Error: {r['error'] or r['status_desc']}\n\n")

    print()
    print(f"Detailed results saved to: command_test_results.txt")

    return 0


if __name__ == "__main__":
    sys.exit(main())
