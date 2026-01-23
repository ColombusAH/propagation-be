#!/usr/bin/env python3
"""
Active polling - send inventory command and read tags.
The device appears to respond with inventory data to ANY command.
"""

import socket
import struct
import sys
import time
from datetime import datetime

HEAD = 0xCF
BROADCAST_ADDR = 0xFF
CMD_INVENTORY = 0x0001
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


def poll_for_tags(ip: str, port: int, duration: int = 30, poll_interval: float = 0.5):
    print("=" * 70)
    print(f"ACTIVE TAG POLLING")
    print(f"Target: {ip}:{port}")
    print(f"Duration: {duration}s, Poll interval: {poll_interval}s")
    print("=" * 70)
    print("\n🏷️  Bring tags close to the reader!\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print(f"Connecting...")
        sock.connect((ip, port))
        print("✓ Connected!\n")

        # Build inventory command
        # CMD: 0x0001, Data: [inv_type, inv_param]
        # inv_type=0x00 (by time), inv_param=0 (single shot)
        frame = struct.pack(">BBHBBB", HEAD, BROADCAST_ADDR, CMD_INVENTORY, 2, 0x00, 0)
        crc = calculate_crc16(frame)
        inventory_cmd = frame + struct.pack("<H", crc)

        print(f"Inventory command: {inventory_cmd.hex().upper()}")
        print("-" * 70)
        print(f"{'Time':<12} {'EPC':<28} {'RSSI':<8} {'Ant'}")
        print("-" * 70)

        start_time = time.time()
        tag_count = 0
        seen_tags = set()
        poll_count = 0

        while time.time() - start_time < duration:
            poll_count += 1

            # Send inventory command
            sock.sendall(inventory_cmd)

            # Read response
            sock.settimeout(1)
            try:
                response = sock.recv(4096)

                if response and len(response) >= 6:
                    # Parse frame
                    if response[0] == HEAD:
                        cmd = (response[2] << 8) | response[3]
                        length = response[4]
                        status = response[5]

                        # Status 0x00 = success with tags, 0x12 = no tags found
                        if cmd == 0x0001 and status == 0x00 and length > 1:
                            payload = response[6 : 6 + length - 1]

                            # Parse tag(s)
                            offset = 0
                            while offset + 5 <= len(payload):
                                rssi = payload[offset]
                                ant = payload[offset + 1]
                                pc = (payload[offset + 2] << 8) | payload[offset + 3]
                                epc_len = payload[offset + 4]

                                if offset + 5 + epc_len <= len(payload):
                                    epc = payload[offset + 5 : offset + 5 + epc_len]
                                    epc_hex = epc.hex().upper()

                                    tag_count += 1
                                    is_new = epc_hex not in seen_tags
                                    seen_tags.add(epc_hex)

                                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                    marker = "🆕" if is_new else "  "

                                    print(
                                        f"{marker}{timestamp}  {epc_hex:<28} {-rssi:>4} dBm  {ant}"
                                    )

                                offset += 5 + epc_len

                        elif status == 0x12:
                            # No tags - this is normal
                            pass

            except socket.timeout:
                pass

            time.sleep(poll_interval)

        print("-" * 70)
        print(f"\n📊 Summary:")
        print(f"   Poll cycles: {poll_count}")
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

    poll_for_tags(ip, port, duration)
