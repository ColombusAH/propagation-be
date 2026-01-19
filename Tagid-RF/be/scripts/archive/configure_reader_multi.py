"""
M-200 Reader Configuration Script for Multi-Tag Detection v2
---------------------------------------------------------
Update: Using simplified parameter structure for Q-value.
"""

import socket
import struct
import time

# Constants
LISTEN_PORT = 4001
HEAD = 0xCF
ADDR = 0x00
POWER_DBM = 30  # Max power


def calculate_crc16(data: bytes) -> int:
    PRESET_VALUE = 0xFFFF
    POLYNOMIAL = 0x8408
    crc_value = PRESET_VALUE
    for byte in data:
        crc_value ^= byte
        for _ in range(8):
            if crc_value & 0x0001:
                crc_value = (crc_value >> 1) ^ POLYNOMIAL
            else:
                crc_value = crc_value >> 1
    return crc_value


def build_frame(cmd: int, data: bytes = b"") -> bytes:
    frame_no_crc = struct.pack(">BBBB", HEAD, ADDR, (cmd >> 8) & 0xFF, cmd & 0xFF)
    frame_no_crc += struct.pack("B", len(data))
    frame_no_crc += data

    crc = calculate_crc16(frame_no_crc)
    return frame_no_crc + struct.pack("<H", crc)


def parse_response(data: bytes):
    if len(data) < 7:
        return False, f"Short frame: {data.hex().upper()}"
    status = data[5]
    return status == 0, f"Status: 0x{status:02X}"


def main():
    print(f"🎧 Waiting for reader on port {LISTEN_PORT}...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen(1)

    try:
        conn, addr = server.accept()
        print(f"✅ Connected to reader: {addr}")
        conn.settimeout(2)

        # 1. Set Query Params (Q=4) using SIMPLE structure
        # Based on m200_protocol.py lines 608: data = struct.pack("BBB", q_value, session, target)
        print("\n1️⃣ Setting Multi-Tag Params (Q=4)...")
        # Q=4, Session=0(S0), Target=0(A)
        query_data = struct.pack("BBB", 4, 0, 0)

        frame = build_frame(0x005B, query_data)  # RFM_SET_QUERY_PARAM
        conn.send(frame)
        time.sleep(0.5)
        resp = conn.recv(1024)
        success, msg = parse_response(resp)
        print(f"   Result: {'Success' if success else 'Failed'} ({msg})")

        # 2. Set Power (30dBm)
        print("\n2️⃣ Setting Max Power (30dBm)...")
        # 0x002F RFM_SET_PWR
        # Data: 1 byte
        pwr_data = bytes([POWER_DBM])
        frame = build_frame(0x002F, pwr_data)
        conn.send(frame)
        time.sleep(0.5)
        resp = conn.recv(1024)
        success, msg = parse_response(resp)
        print(f"   Result: {'Success' if success else 'Failed'} ({msg})")

        print("\n✅ Configuration Complete! Please restart the server.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        server.close()


if __name__ == "__main__":
    main()
