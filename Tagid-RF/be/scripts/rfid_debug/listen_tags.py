#!/usr/bin/env python3
"""
Real-time tag listener - captures tags as they are scanned.
The device appears to send inventory data automatically when tags are read.
"""

import socket
import struct
import sys
import time
from datetime import datetime

HEAD = 0xCF
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408


def parse_inventory_response(data: bytes) -> list:
    """
    Parse inventory response from M-200.

    Format per tag:
    - RSSI (1 byte) - signal strength
    - Ant (1 byte) - antenna number
    - PC (2 bytes, big-endian) - Protocol Control
    - EPC Length (1 byte) - in bytes
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
                "antenna": ant,
                "pc": f"{pc:04X}",
                "epc_length": epc_len,
            }
        )

        offset += 5 + epc_len

    return tags


def listen_for_tags(ip: str, port: int, duration: int = 60):
    print("=" * 70)
    print(f"RFID TAG LISTENER")
    print(f"Target: {ip}:{port}")
    print(f"Duration: {duration} seconds")
    print("=" * 70)
    print("\n🏷️  Bring tags close to the reader to scan them!\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print(f"Connecting to {ip}:{port}...")
        sock.connect((ip, port))
        print("✓ Connected!\n")

        print("-" * 70)
        print(f"{'Time':<12} {'EPC':<28} {'RSSI':<8} {'Ant':<4}")
        print("-" * 70)

        sock.settimeout(2)
        start_time = time.time()
        tag_count = 0
        seen_tags = set()

        while time.time() - start_time < duration:
            try:
                data = sock.recv(4096)

                if data and len(data) >= 6:
                    # Parse frame(s) - might have multiple
                    offset = 0
                    while offset < len(data):
                        if offset + 6 > len(data):
                            break

                        if data[offset] != HEAD:
                            offset += 1
                            continue

                        addr = data[offset + 1]
                        cmd = struct.unpack(">H", data[offset + 2 : offset + 4])[0]
                        data_len = data[offset + 4]
                        status = data[offset + 5]

                        frame_size = 5 + data_len + 2  # header + data_len bytes + CRC
                        if offset + frame_size > len(data):
                            break

                        # Check if this is an inventory response
                        if cmd == 0x0001 and status == 0x00:
                            # Parse tag data (after status byte)
                            payload = data[offset + 6 : offset + 5 + data_len]
                            tags = parse_inventory_response(payload)

                            for tag in tags:
                                tag_count += 1
                                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                epc = tag["epc"]

                                # Mark new tags
                                is_new = epc not in seen_tags
                                seen_tags.add(epc)
                                marker = "🆕" if is_new else "  "

                                print(
                                    f"{marker}{timestamp}  {epc:<28} {tag['rssi']:>4} dBm  {tag['antenna']}"
                                )

                        offset += frame_size

            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(0.5)

        print("-" * 70)
        print(f"\n📊 Summary:")
        print(f"   Total reads: {tag_count}")
        print(f"   Unique tags: {len(seen_tags)}")
        if seen_tags:
            print(f"\n   Unique EPCs:")
            for epc in sorted(seen_tags):
                print(f"   - {epc}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        sock.close()
        print("\nSocket closed")


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    listen_for_tags(ip, port, duration)
