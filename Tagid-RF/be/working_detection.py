import re
import socket
import struct
import time

# Listen on the port the reader connects to
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 2022  # Reader is configured for port 2022!


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


def build_command(cmd_code: int, data: bytes = b"", addr: int = 0xFF) -> bytes:
    head = 0xCF
    frame_body = struct.pack(">BBBB", head, addr, (cmd_code >> 8) & 0xFF, cmd_code & 0xFF)
    frame_body += struct.pack("B", len(data))
    frame_body += data
    crc = calculate_crc16(frame_body)
    return frame_body + struct.pack(">H", crc)


def extract_epcs_from_raw(data: bytes) -> list:
    """Extract EPCs from raw data - looking for E2 80 68 94 pattern"""
    epcs = []

    # The tags we saw all start with E2 80 68 94 00 00
    # Search for this pattern
    pattern = b"\xe2\x80\x68\x94"

    i = 0
    while i < len(data) - 12:
        # Look for the known prefix
        if data[i : i + 4] == pattern:
            # Extract 12-byte EPC
            epc = data[i : i + 12].hex().upper()
            if epc not in epcs:
                epcs.append(epc)
            i += 12
        else:
            i += 1

    return epcs


def main():
    print("=" * 60)
    print("WORKING TAG DETECTION")
    print("Based on manufacturer software success (16 tags!)")
    print("=" * 60)
    print(f"\nListening on {LISTEN_IP}:{LISTEN_PORT}...")
    print("If no connection, try changing LISTEN_PORT to 2022")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)

    print("Waiting for reader connection...")
    print("(Power cycle reader if needed)")

    conn, addr = server.accept()
    print(f"[+] Connected: {addr[0]}:{addr[1]}")

    # Collect all unique tags
    all_tags = {}

    print("\n📡 Listening for Tags (120 seconds)...")
    print("   Move tags through the gate!")
    print("-" * 60)

    conn.settimeout(1.0)
    buffer = b""
    frame_count = 0
    start_time = time.time()

    try:
        while time.time() - start_time < 120:
            try:
                chunk = conn.recv(4096)
                if not chunk:
                    break

                # Process raw data to find EPCs
                epcs = extract_epcs_from_raw(chunk)
                for epc in epcs:
                    if epc not in all_tags:
                        all_tags[epc] = {"count": 0, "first_seen": time.time() - start_time}
                        print(f"🆕 TAG #{len(all_tags)}: {epc}")
                    all_tags[epc]["count"] += 1

                # Also try frame parsing
                buffer += chunk
                while len(buffer) >= 7:
                    if buffer[0] != 0xCF:
                        # Try to find EPCs in non-frame data
                        epcs = extract_epcs_from_raw(buffer[:100])
                        for epc in epcs:
                            if epc not in all_tags:
                                all_tags[epc] = {"count": 0, "first_seen": time.time() - start_time}
                                print(f"🆕 TAG #{len(all_tags)}: {epc} (raw)")
                            all_tags[epc]["count"] += 1

                        idx = buffer.find(b"\xcf", 1)
                        if idx != -1:
                            buffer = buffer[idx:]
                        else:
                            buffer = b""
                        continue

                    length = buffer[4]
                    if len(buffer) < 7 + length:
                        break

                    frame = buffer[: 7 + length]
                    buffer = buffer[7 + length :]
                    frame_count += 1

                    # Try to extract EPCs from frame payload
                    payload = frame[6:-2]
                    epcs = extract_epcs_from_raw(payload)
                    for epc in epcs:
                        if epc not in all_tags:
                            all_tags[epc] = {"count": 0, "first_seen": time.time() - start_time}
                            print(f"🆕 TAG #{len(all_tags)}: {epc} (frame)")
                        all_tags[epc]["count"] += 1

                # Progress update every 10 seconds
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 and elapsed > 0:
                    print(f"   [{elapsed}s] Tags found: {len(all_tags)}")

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        pass

    print("-" * 60)
    print(f"\n{'='*60}")
    print(f"=== FINAL SUMMARY ===")
    print(f"{'='*60}")
    print(f"Total Frames: {frame_count}")
    print(f"Unique Tags: {len(all_tags)}")
    print()

    if all_tags:
        print("Detected Tags:")
        for i, (epc, data) in enumerate(sorted(all_tags.items()), 1):
            print(f"  {i:2}. {epc} (seen {data['count']}x)")
    else:
        print("No tags detected. Try:")
        print("  1. Change LISTEN_PORT to 2022")
        print("  2. Update Remote IP in reader's Network Settings to your PC's IP")
        print("  3. Power cycle the reader")

    conn.close()
    server.close()


if __name__ == "__main__":
    main()
