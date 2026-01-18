#!/usr/bin/env python3
"""
Raw data capture - just capture and log everything we receive.
"""

import socket
import sys
import time
from datetime import datetime

HEAD = 0xCF


def capture_raw(ip: str, port: int, duration: int = 30):
    print("=" * 70)
    print(f"RAW DATA CAPTURE")
    print(f"Target: {ip}:{port}")
    print(f"Duration: {duration} seconds")
    print("=" * 70)
    print("\n🏷️  Bring tags close to the reader!\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print(f"Connecting...")
        sock.connect((ip, port))
        print("✓ Connected!\n")

        sock.settimeout(2)
        start_time = time.time()
        message_count = 0

        while time.time() - start_time < duration:
            try:
                data = sock.recv(4096)

                if data:
                    message_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

                    print(f"\n[{timestamp}] Message #{message_count} ({len(data)} bytes)")
                    print(f"  HEX: {data.hex().upper()}")

                    # Parse if starts with HEAD
                    if len(data) >= 6 and data[0] == HEAD:
                        addr = data[1]
                        cmd = (data[2] << 8) | data[3]
                        length = data[4]
                        status = data[5] if len(data) > 5 else 0

                        print(f"  RFID Frame:")
                        print(f"    ADDR:   0x{addr:02X}")
                        print(f"    CMD:    0x{cmd:04X}")
                        print(f"    LEN:    {length}")
                        print(f"    STATUS: 0x{status:02X}")

                        # If STATUS is 0x00 (success), parse payload
                        if status == 0x00 and length > 1:
                            payload = data[6 : 6 + length - 1]
                            print(f"    PAYLOAD: {payload.hex().upper()}")

                            # Try to extract EPC from inventory
                            if cmd == 0x0001 and len(payload) >= 5:
                                rssi = payload[0]
                                ant = payload[1]
                                pc = (payload[2] << 8) | payload[3]
                                epc_len = payload[4]
                                if len(payload) >= 5 + epc_len:
                                    epc = payload[5 : 5 + epc_len]
                                    print(f"\n    📍 TAG DETECTED!")
                                    print(f"       EPC:  {epc.hex().upper()}")
                                    print(f"       RSSI: {-rssi} dBm")
                                    print(f"       ANT:  {ant}")
                                    print(f"       PC:   0x{pc:04X}")

                    # Also try ASCII
                    try:
                        ascii_view = data.decode("ascii", errors="replace")
                        printable = "".join(c if c.isprintable() else "." for c in ascii_view)
                        if any(c.isalnum() for c in printable):
                            print(f"  ASCII: {printable}")
                    except:
                        pass

            except socket.timeout:
                continue

        print("\n" + "=" * 70)
        print(f"Captured {message_count} messages in {duration} seconds")
        print("=" * 70)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        sock.close()
        print("Socket closed")


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    capture_raw(ip, port, duration)
