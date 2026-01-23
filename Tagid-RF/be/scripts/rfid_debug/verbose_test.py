#!/usr/bin/env python3
"""
Verbose reader - logs everything sent and received.
"""

import socket
import struct
import sys
import time

HEAD = 0xCF
BROADCAST_ADDR = 0xFF
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408


def calculate_crc16(data: bytes) -> int:
    crc_value = PRESET_VALUE
    for byte in data:
        crc_value ^= byte
        for _ in range(8):
            if crc_value & 0x0001:
                crc_value = (crc_value >> 1) ^ POLYNOMIAL
            else:
                crc_value = crc_value >> 1
    return crc_value


def build_command(cmd: int, data: bytes = b"") -> bytes:
    frame = struct.pack(">BBHB", HEAD, BROADCAST_ADDR, cmd, len(data)) + data
    crc = calculate_crc16(frame)
    return frame + struct.pack("<H", crc)


def send_and_receive(sock: socket.socket, cmd_hex: int, cmd_name: str, data: bytes = b""):
    """Send command and print response"""
    cmd_bytes = build_command(cmd_hex, data)

    timestamp = time.strftime("%H:%M:%S")
    print(f"\n[{timestamp}] ➡️  SENDING: {cmd_name} (0x{cmd_hex:04X})")
    print(f"           TX: {cmd_bytes.hex().upper()}")

    sock.sendall(cmd_bytes)

    # Read response
    sock.settimeout(3)
    try:
        response = sock.recv(4096)

        if response:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] ⬅️  RECEIVED: {len(response)} bytes")
            print(f"           RX: {response.hex().upper()}")

            # Parse frame
            if len(response) >= 6 and response[0] == HEAD:
                addr = response[1]
                resp_cmd = (response[2] << 8) | response[3]
                length = response[4]
                status = response[5]

                print(
                    f"           PARSED: ADDR=0x{addr:02X}, CMD=0x{resp_cmd:04X}, LEN={length}, STATUS=0x{status:02X}"
                )

                # Status description
                status_desc = {
                    0x00: "SUCCESS",
                    0x01: "PARAM_ERROR",
                    0x02: "COMMAND_FAILED",
                    0x12: "INVENTORY_COMPLETE (no tags)",
                    0x14: "TAG_TIMEOUT",
                }.get(status, f"UNKNOWN")
                print(f"           STATUS: {status_desc}")

                # If inventory with tags
                if resp_cmd == 0x0001 and status == 0x00 and length > 1:
                    payload = response[6 : 6 + length - 1]
                    print(f"           PAYLOAD: {payload.hex().upper()}")

                    # Parse tags
                    offset = 0
                    tag_num = 0
                    while offset + 5 <= len(payload):
                        rssi = payload[offset]
                        ant = payload[offset + 1]
                        epc_len = payload[offset + 4]

                        if offset + 5 + epc_len <= len(payload):
                            tag_num += 1
                            epc = payload[offset + 5 : offset + 5 + epc_len].hex().upper()
                            print(f"\n           📍 TAG #{tag_num}:")
                            print(f"              EPC:  {epc}")
                            print(f"              RSSI: {-rssi} dBm")
                            print(f"              ANT:  {ant}")

                        offset += 5 + epc_len

                # If device info response
                elif resp_cmd == 0x0070 and status == 0x00 and length > 1:
                    payload = response[6 : 6 + length - 1]
                    try:
                        # Try to extract ASCII strings
                        text = payload.rstrip(b"\x00").decode("ascii", errors="replace")
                        print(f"           INFO: {text[:100]}...")
                    except:
                        pass

                return response
        else:
            print(f"           (empty response)")

    except socket.timeout:
        print(f"           ⏰ TIMEOUT")

    return None


def verbose_test(ip: str, port: int):
    print("=" * 70)
    print(f"VERBOSE RFID READER TEST")
    print(f"Target: {ip}:{port}")
    print("=" * 70)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        timestamp = time.strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 🔌 CONNECTING to {ip}:{port}...")
        sock.connect((ip, port))
        print(f"           ✓ Connected!")

        # Check for buffered data
        time.sleep(0.2)
        sock.setblocking(False)
        try:
            buffered = sock.recv(4096)
            if buffered:
                timestamp = time.strftime("%H:%M:%S")
                print(f"\n[{timestamp}] ⬅️  BUFFERED DATA: {len(buffered)} bytes")
                print(f"           RX: {buffered.hex().upper()}")
        except:
            pass
        sock.setblocking(True)

        # Test commands
        print("\n" + "=" * 70)
        print("COMMAND TESTS")
        print("=" * 70)

        # 1. Get Device Info
        send_and_receive(sock, 0x0070, "GET_DEVICE_INFO")
        time.sleep(0.5)

        # 2. Get All Parameters
        send_and_receive(sock, 0x0052, "GET_ALL_PARAM")
        time.sleep(0.5)

        # 3. Inventory (single shot)
        send_and_receive(sock, 0x0001, "INVENTORY", b"\x00\x01")  # type=0, count=1
        time.sleep(0.5)

        # 4. Inventory with different params
        send_and_receive(sock, 0x0001, "INVENTORY (alt)", b"\x01\x01")  # type=1, count=1
        time.sleep(0.5)

        # 5. Try to read any remaining data
        print("\n" + "=" * 70)
        print("PASSIVE LISTEN (10s)")
        print("=" * 70)
        print("\n🏷️  Bring tags close to the reader now!")

        start = time.time()
        while time.time() - start < 10:
            try:
                sock.settimeout(1)
                data = sock.recv(4096)
                if data:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"\n[{timestamp}] ⬅️  RECEIVED: {len(data)} bytes")
                    print(f"           RX: {data.hex().upper()}")

                    if len(data) >= 6 and data[0] == HEAD:
                        cmd = (data[2] << 8) | data[3]
                        status = data[5]
                        print(f"           CMD=0x{cmd:04X}, STATUS=0x{status:02X}")
            except socket.timeout:
                continue

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
    finally:
        sock.close()
        print("\n" + "=" * 70)
        print("Socket closed")
        print("=" * 70)


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    verbose_test(ip, port)
