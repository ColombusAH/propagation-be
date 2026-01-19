#!/usr/bin/env python3
"""
Raw socket test - send command and read everything we get back.
Use same approach as rfid_reader.py service.
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


def test_raw_socket(ip: str, port: int):
    print("=" * 70)
    print(f"Raw Socket Test")
    print(f"Target: {ip}:{port}")
    print("=" * 70)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print(f"\n1. Connecting...")
        sock.connect((ip, port))
        print(f"   ✓ Connected!")

        # Wait for device to stabilize
        time.sleep(0.1)

        # Clear any buffered data
        print("\n2. Checking for buffered data...")
        sock.setblocking(False)
        try:
            buffered = sock.recv(4096)
            if buffered:
                print(f"   Found {len(buffered)} buffered bytes:")
                print(f"   HEX: {buffered.hex().upper()}")
        except BlockingIOError:
            print("   No buffered data")
        sock.setblocking(True)
        sock.settimeout(10)

        # Build command with CRC in BOTH endianness
        print("\n3. Testing GET_DEVICE_INFO (0x0070) with different CRC formats...")

        frame_base = struct.pack(">BBHB", HEAD, BROADCAST_ADDR, 0x0070, 0)
        crc = calculate_crc16(frame_base)

        # Try little-endian CRC
        cmd_le = frame_base + struct.pack("<H", crc)
        print(f"\n   a) Little-endian CRC:")
        print(f"      TX: {cmd_le.hex().upper()}")
        sock.sendall(cmd_le)

        # Wait and collect
        sock.settimeout(3)
        try:
            response = sock.recv(4096)
            if response:
                print(f"      RX: {response.hex().upper()} ({len(response)} bytes)")
                analyze_response(response)
            else:
                print("      No response (connection closed)")
        except socket.timeout:
            print("      TIMEOUT")

        time.sleep(0.5)

        # Try big-endian CRC
        cmd_be = frame_base + struct.pack(">H", crc)
        print(f"\n   b) Big-endian CRC:")
        print(f"      TX: {cmd_be.hex().upper()}")
        sock.sendall(cmd_be)

        sock.settimeout(3)
        try:
            response = sock.recv(4096)
            if response:
                print(f"      RX: {response.hex().upper()} ({len(response)} bytes)")
                analyze_response(response)
            else:
                print("      No response")
        except socket.timeout:
            print("      TIMEOUT")

        # Try inventory command which worked partially before
        print("\n4. Testing INVENTORY command (0x0001)...")
        frame_inv = struct.pack(">BBHBBB", HEAD, BROADCAST_ADDR, 0x0001, 2, 0x00, 0)
        crc_inv = calculate_crc16(frame_inv)
        cmd_inv = frame_inv + struct.pack("<H", crc_inv)
        print(f"   TX: {cmd_inv.hex().upper()}")
        sock.sendall(cmd_inv)

        sock.settimeout(5)
        try:
            response = sock.recv(4096)
            if response:
                print(f"   RX: {response.hex().upper()} ({len(response)} bytes)")
                analyze_response(response)
            else:
                print("   No response")
        except socket.timeout:
            print("   TIMEOUT")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        sock.close()
        print("\nSocket closed")


def analyze_response(data: bytes):
    """Try to analyze response"""
    if len(data) >= 6 and data[0] == HEAD:
        addr = data[1]
        cmd = struct.unpack(">H", data[2:4])[0]
        length = data[4]
        status = data[5]
        print(f"   RFID Frame detected:")
        print(f"      ADDR:   0x{addr:02X}")
        print(f"      CMD:    0x{cmd:04X}")
        print(f"      LEN:    {length}")
        print(f"      STATUS: 0x{status:02X}")
        if len(data) > 6:
            payload = data[6:-2] if len(data) > 8 else data[6:]
            if payload:
                print(f"      DATA:   {payload.hex().upper()}")
                # Try to decode as ASCII
                try:
                    ascii_str = payload.rstrip(b"\x00").decode(
                        "ascii", errors="replace"
                    )
                    if any(c.isalnum() for c in ascii_str):
                        print(f"      ASCII:  {ascii_str}")
                except:
                    pass
        return True
    else:
        # Check if ASCII
        try:
            ascii_view = data.decode("ascii", errors="replace")
            printable = "".join(
                c if c.isprintable() or c in "\n\r\t" else "." for c in ascii_view
            )
            if printable.strip():
                print(f"   ASCII: {printable[:200]}")
        except:
            pass
        return False


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    test_raw_socket(ip, port)
