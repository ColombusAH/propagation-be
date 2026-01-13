"""
M-200 Reader Configuration Checker
----------------------------------
Connects to the reader (waiting for it to connect in push mode)
and queries all parameters using RFM_GET_ALL_PARAM (0x0052).
Parses the result to show current Config, specifically WorkMode.
"""

import socket
import time
import struct

LISTEN_PORT = 4001
HEAD = 0xCF
ADDR = 0x00

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

def parse_device_param(data: bytes):
    # Based on DeviceParam.cs:
    # 0: ADDR, 1: PRO, 2: WORKMODE, 3: INTERFACE, 4: BAUD, 5: WG, 6: ANT, 7: REGION
    # 8-9: START_F_I, 10-11: START_F_D, 12-13: STEP_F
    # 14: CN, 15: POWER, 16: AREA, 17: Q, 18: SESSION, 19: STARTADDR, 20: DATALEN
    # 21: FILTERTIME, 22: TRIGTIME, 23: BUZZER, 24: INTERVAL
    
    if len(data) < 25:
        print(f"⚠️ Response too short: {len(data)} (expected ~25+)")
        print(data.hex().upper())
        return

    print("\n📊 Current Reader Configuration:")
    print(f"   ADDR: 0x{data[0]:02X}")
    print(f"   Protocol: 0x{data[1]:02X}")
    
    wm = data[2]
    wm_str = {0: "Answer (Passive)", 1: "Auto (Active)", 2: "Trigger (Gate)"}.get(wm, "Unknown")
    print(f"   WorkMode: {wm} ({wm_str})  <-- CRITICAL")
    
    print(f"   Interface: 0x{data[3]:02X}")
    print(f"   Antenna: 0x{data[6]:02X}")
    print(f"   Power: {data[15]} dBm")
    print(f"   Q-Value: {data[17]}")
    print(f"   Session: {data[18]}")
    print(f"   FilterTime: {data[21]}s")
    print(f"   Interval: {data[24]}s")

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
        
        print("\n🔍 Querying All Parameters (0x0052)...")
        frame = build_frame(0x0052)
        conn.send(frame)
        time.sleep(0.5)
        
        resp = conn.recv(1024)
        if len(resp) < 7:
             print("❌ No valid response")
        else:
            status = resp[5]
            if status == 0:
                # Data starts at index 6
                # Length of data is at index 4
                data_len = resp[4] - 1 # len includes status
                payload = resp[6:6+data_len]
                parse_device_param(payload)
            else:
                print(f"❌ Command Failed. Status: 0x{status:02X}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main()
