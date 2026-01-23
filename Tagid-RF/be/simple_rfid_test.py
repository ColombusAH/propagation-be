"""
RFID Tag Reader - Improved version with longer timeout and multiple inventory attempts.
"""

import socket
import struct
import sys
import time
from datetime import datetime

# Constants
HEAD = 0xCF
BROADCAST_ADDR = 0xFF
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408

LOG_FILE = "rfid_debug_log.txt"


def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def calculate_crc16(data):
    crc = PRESET_VALUE
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ POLYNOMIAL
            else:
                crc = crc >> 1
    return crc


def build_command(cmd, data=b"", addr=BROADCAST_ADDR):
    frame = struct.pack(">BBHB", HEAD, addr, cmd, len(data)) + data
    crc = calculate_crc16(frame)
    frame += struct.pack(">H", crc)
    return frame


def hex_dump(label, data, direction=""):
    hex_str = " ".join(f"{b:02X}" for b in data)
    log(f"  {direction} {label}: {hex_str} ({len(data)} bytes)")


def parse_frame(data):
    """Parse M-200 response frame and show details."""
    if len(data) < 6:
        log(f"  Frame too short: {len(data)} bytes")
        return None

    log(f"  Frame analysis:")
    log(f"    HEAD   = 0x{data[0]:02X}")
    log(f"    ADDR   = 0x{data[1]:02X}")
    cmd = struct.unpack(">H", data[2:4])[0]
    log(f"    CMD    = 0x{cmd:04X}")
    data_len = data[4]
    log(f"    LEN    = {data_len}")
    if len(data) > 5:
        status = data[5]
        log(f"    STATUS = 0x{status:02X}")
        return {
            "cmd": cmd,
            "len": data_len,
            "status": status,
            "data": data[6 : 6 + data_len - 1] if data_len > 1 else b"",
        }
    return None


def main():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== RFID Debug Log - {datetime.now()} ===\n\n")

    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022

    log(f"Target: {ip}:{port}")
    log("")

    # Connect
    log("=" * 60)
    log("STEP 1: TCP Connection")
    log("=" * 60)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)  # Longer timeout
        sock.connect((ip, port))
        log(f"  [OK] Connected to {ip}:{port}")
    except Exception as e:
        log(f"  [FAIL] {e}")
        return 1

    log("")

    # Wait for any buffered data
    log("Clearing buffer...")
    sock.setblocking(False)
    try:
        buffered = sock.recv(4096)
        if buffered:
            hex_dump("Buffered data", buffered, "<--")
    except BlockingIOError:
        log("  No buffered data")
    sock.setblocking(True)
    sock.settimeout(10.0)

    log("")

    # Command 1: Get Device Info
    log("=" * 60)
    log("STEP 2: Get Device Info (CMD 0x0070)")
    log("=" * 60)
    cmd = build_command(0x0070)
    hex_dump("TX", cmd, "-->")

    try:
        sock.sendall(cmd)
        response = sock.recv(1024)
        hex_dump("RX", response, "<--")
        parsed = parse_frame(response)
        if parsed and parsed["status"] == 0x00:
            log("  [OK] Device responded successfully")
    except Exception as e:
        log(f"  [FAIL] {e}")

    log("")

    # Try different inventory approaches
    inventory_attempts = [
        ("Inventory by time (1 sec)", bytes([0x00, 0x01])),
        ("Inventory by count (5 cycles)", bytes([0x01, 0x05])),
        ("Inventory continuous", bytes([0x00, 0x00])),
    ]

    for attempt_name, inv_data in inventory_attempts:
        log("=" * 60)
        log(f"STEP 3: {attempt_name} (CMD 0x0001)")
        log("=" * 60)

        cmd = build_command(0x0001, inv_data)
        hex_dump("TX", cmd, "-->")

        try:
            sock.sendall(cmd)
            log("  Waiting for response (10 sec timeout)...")

            # Try to read multiple times
            total_data = b""
            start_time = time.time()

            while time.time() - start_time < 8:  # 8 second window
                try:
                    sock.settimeout(2.0)  # 2 second per read
                    chunk = sock.recv(1024)
                    if chunk:
                        total_data += chunk
                        hex_dump("RX chunk", chunk, "<--")

                        # Check if we got a complete response
                        if len(total_data) >= 6 and total_data[0] == HEAD:
                            parsed = parse_frame(total_data)
                            if parsed:
                                if parsed["status"] == 0x00:
                                    log("  [OK] TAGS FOUND!")
                                    if parsed["data"]:
                                        log(
                                            f"  Tag data: {parsed['data'].hex().upper()}"
                                        )
                                        # Parse first tag
                                        td = parsed["data"]
                                        if len(td) >= 5:
                                            log(f"    RSSI: -{td[0]} dBm")
                                            log(f"    Antenna: {td[1]}")
                                            epc_len = td[4]
                                            if len(td) >= 5 + epc_len:
                                                epc = td[5 : 5 + epc_len]
                                                log(f"    EPC: {epc.hex().upper()}")
                                    break
                                elif parsed["status"] == 0x12:
                                    log("  [INFO] Inventory complete - no tags")
                                    break
                                elif parsed["status"] == 0x14:
                                    log("  [INFO] Tag timeout")
                                    break
                except socket.timeout:
                    if total_data:
                        log("  No more data...")
                    continue

            if not total_data:
                log("  [INFO] No response received")

        except Exception as e:
            log(f"  [FAIL] {e}")

        log("")

        # Send stop inventory command between attempts
        stop_cmd = build_command(0x0028)
        try:
            sock.sendall(stop_cmd)
            time.sleep(0.5)
            sock.setblocking(False)
            try:
                sock.recv(1024)
            except BlockingIOError:
                pass
            sock.setblocking(True)
            sock.settimeout(10.0)
        except:
            pass

        # Only try first successful method
        if total_data and len(total_data) >= 6:
            break

    # Disconnect
    log("=" * 60)
    log("STEP 4: Disconnecting")
    log("=" * 60)
    sock.close()
    log("  [OK] Disconnected")
    log("")
    log(f"Full log saved to: {LOG_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
