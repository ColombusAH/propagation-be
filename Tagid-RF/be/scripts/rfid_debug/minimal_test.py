#!/usr/bin/env python3
"""
Minimal test - replicate exact behavior from debug_reader.py that worked.
Just connect, send ONE command, print raw response.
"""

import socket
import struct
import sys

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


def minimal_test(ip: str, port: int):
    print(f"Connecting to {ip}:{port}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((ip, port))
    print("Connected!")

    # Test 1: Just read without sending anything (in case auto-mode)
    print("\n1. Checking for unsolicited data (2s timeout)...")
    sock.settimeout(2)
    try:
        data = sock.recv(4096)
        if data:
            print(f"   Received: {data.hex().upper()} ({len(data)} bytes)")
        else:
            print("   (none)")
    except socket.timeout:
        print("   (none - timeout)")

    # Test 2: Send get device info (0x0070)
    print("\n2. Sending GET_DEVICE_INFO (0x0070)...")
    frame = struct.pack(">BBHB", HEAD, BROADCAST_ADDR, 0x0070, 0)
    crc = calculate_crc16(frame)
    cmd = frame + struct.pack("<H", crc)
    print(f"   TX: {cmd.hex().upper()}")
    sock.sendall(cmd)

    sock.settimeout(3)
    try:
        data = sock.recv(4096)
        print(f"   RX: {data.hex().upper()} ({len(data)} bytes)")
        parse_response(data)
    except socket.timeout:
        print("   TIMEOUT")

    # Test 3: Send inventory (0x0001) with data
    print("\n3. Sending INVENTORY (0x0001) with params...")
    frame = struct.pack(">BBHBBB", HEAD, BROADCAST_ADDR, 0x0001, 2, 0x00, 1)
    crc = calculate_crc16(frame)
    cmd = frame + struct.pack("<H", crc)
    print(f"   TX: {cmd.hex().upper()}")
    sock.sendall(cmd)

    sock.settimeout(3)
    try:
        data = sock.recv(4096)
        print(f"   RX: {data.hex().upper()} ({len(data)} bytes)")
        parse_response(data)
    except socket.timeout:
        print("   TIMEOUT")

    # Test 4: Try different inventory format (no params)
    print("\n4. Sending INVENTORY (0x0001) without params...")
    frame = struct.pack(">BBHB", HEAD, BROADCAST_ADDR, 0x0001, 0)
    crc = calculate_crc16(frame)
    cmd = frame + struct.pack("<H", crc)
    print(f"   TX: {cmd.hex().upper()}")
    sock.sendall(cmd)

    sock.settimeout(3)
    try:
        data = sock.recv(4096)
        print(f"   RX: {data.hex().upper()} ({len(data)} bytes)")
        parse_response(data)
    except socket.timeout:
        print("   TIMEOUT")

    # Test 5: Get all params (0x0052)
    print("\n5. Sending GET_ALL_PARAM (0x0052)...")
    frame = struct.pack(">BBHB", HEAD, BROADCAST_ADDR, 0x0052, 0)
    crc = calculate_crc16(frame)
    cmd = frame + struct.pack("<H", crc)
    print(f"   TX: {cmd.hex().upper()}")
    sock.sendall(cmd)

    sock.settimeout(3)
    try:
        data = sock.recv(4096)
        print(f"   RX: {data.hex().upper()} ({len(data)} bytes)")
        parse_response(data)
    except socket.timeout:
        print("   TIMEOUT")

    sock.close()
    print("\nDone.")


def parse_response(data: bytes):
    if len(data) >= 6 and data[0] == HEAD:
        addr = data[1]
        cmd = (data[2] << 8) | data[3]
        length = data[4]
        status = data[5]

        print(f"   Parsed: ADDR=0x{addr:02X}, CMD=0x{cmd:04X}, LEN={length}, STATUS=0x{status:02X}")

        if status == 0x00 and length > 1:
            payload = data[6 : 6 + length - 1]
            print(f"   Payload: {payload.hex().upper()}")

            # If inventory response, try to extract EPC
            if cmd == 0x0001 and len(payload) >= 5:
                rssi = payload[0]
                ant = payload[1]
                epc_len = payload[4]
                if len(payload) >= 5 + epc_len:
                    epc = payload[5 : 5 + epc_len].hex().upper()
                    print(f"\n   📍 TAG: EPC={epc}, RSSI={-rssi}dBm, ANT={ant}")


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    minimal_test(ip, port)
