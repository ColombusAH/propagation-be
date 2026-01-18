import socket
import struct
import time
import sys

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4001
TARGET_TAGS = 16
LISTEN_TIME = 20  # seconds per test


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


def wait_for_response(client, expected_cmd, timeout=3.0):
    client.settimeout(timeout)
    start_time = time.time()
    buffer = b""
    try:
        while time.time() - start_time < timeout:
            chunk = client.recv(4096)
            if not chunk:
                break
            buffer += chunk
            while len(buffer) >= 7:
                if buffer[0] != 0xCF:
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
                cmd = (frame[2] << 8) | frame[3]
                status = frame[5]
                if cmd == expected_cmd:
                    return True, status, frame[6:-2]
                elif cmd == 0x0082:
                    continue
    except socket.timeout:
        return False, "Timeout", None
    return False, "Not Found", None


def parse_tag(payload):
    if len(payload) < 5:
        return None
    epc = payload[5 : 5 + payload[4]]
    return epc.hex().upper() if epc else None


def listen_for_tags(conn, duration):
    """Listen for tags and return set of unique EPCs"""
    conn.settimeout(duration + 1)
    buffer = b""
    tags = set()
    start = time.time()

    try:
        while time.time() - start < duration:
            try:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                while len(buffer) >= 7:
                    if buffer[0] != 0xCF:
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
                    cmd = (frame[2] << 8) | frame[3]
                    status = frame[5]
                    payload = frame[6:-2]

                    if cmd in [0x0082, 0x0001] and status == 0x00:
                        epc = parse_tag(payload)
                        if epc and len(epc) >= 4:
                            tags.add(epc)
            except socket.timeout:
                break
    except Exception as e:
        print(f"   Error: {e}")

    return tags


def apply_config(conn, workmode, q_value, session, gatemode):
    """Apply configuration and return success status"""

    # 1. Read current all params
    conn.send(build_command(0x0072))
    success, status, data = wait_for_response(conn, 0x0072)
    if not success or not data or len(data) < 20:
        return False

    # 2. Modify params
    new_params = bytearray(data)
    new_params[2] = workmode
    new_params[17] = q_value
    new_params[18] = session

    # 3. Set new params
    conn.send(build_command(0x0071, bytes(new_params)))
    success, status, _ = wait_for_response(conn, 0x0071)
    if not success or status != 0x00:
        return False

    # 4. Set Gate WorkParam (GATEMODE)
    gate_payload = b"\x01" + bytes([gatemode]) + b"\x00" * 16
    conn.send(build_command(0x0083, gate_payload))
    success, status, _ = wait_for_response(conn, 0x0083)

    return True


def main():
    print("=" * 60)
    print("AUTO-TUNE: Systematic Configuration Search")
    print(f"Target: {TARGET_TAGS} unique tags")
    print(f"Listen time per test: {LISTEN_TIME} seconds")
    print("=" * 60)

    # Configuration combinations to try
    configs = []

    # Priority 1: WorkMode variations with optimal Q and Session
    for wm in [1, 0, 2]:  # Active, Answer, Trigger
        for q in [7, 6, 5, 8, 4]:
            for s in [0, 1, 2]:  # Session 0, 1, 2
                for gm in [0, 1]:  # Inventory, EAS
                    configs.append(
                        {
                            "workmode": wm,
                            "q": q,
                            "session": s,
                            "gatemode": gm,
                            "desc": f"WM={wm} Q={q} S={s} GM={gm}",
                        }
                    )

    print(f"\nTotal configurations to test: {len(configs)}")
    print("⚠️ IMPORTANT: Move tags through the gate during each test!")
    print("-" * 60)

    best_result = {"tags": 0, "config": None}

    for i, cfg in enumerate(configs, 1):
        print(f"\n[{i}/{len(configs)}] Testing: {cfg['desc']}")

        try:
            # Create new server for each test
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.settimeout(30)
            server.bind((LISTEN_IP, LISTEN_PORT))
            server.listen(1)

            print("   Waiting for reader connection...")
            try:
                conn, addr = server.accept()
                print(f"   Connected: {addr[0]}")
            except socket.timeout:
                print("   ❌ Connection timeout. Power cycle the reader!")
                server.close()
                continue

            # Apply configuration
            print(f"   Applying config...")
            success = apply_config(conn, cfg["workmode"], cfg["q"], cfg["session"], cfg["gatemode"])
            if not success:
                print("   ❌ Failed to apply config")
                conn.close()
                server.close()
                continue

            # Start inventory
            inv_payload = b"\x00\x00\x00\x00\x00"
            conn.send(build_command(0x0001, inv_payload))

            # Listen for tags
            print(f"   📡 Listening for {LISTEN_TIME}s... MOVE TAGS NOW!")
            tags = listen_for_tags(conn, LISTEN_TIME)

            print(f"   ✅ Found {len(tags)} unique tags")

            if len(tags) > best_result["tags"]:
                best_result["tags"] = len(tags)
                best_result["config"] = cfg
                print(f"   🎉 NEW BEST! {len(tags)} tags")

            if len(tags) >= TARGET_TAGS:
                print("\n" + "=" * 60)
                print(f"🏆 SUCCESS! Found {len(tags)}/{TARGET_TAGS} tags!")
                print(f"Optimal config: {cfg['desc']}")
                print("=" * 60)
                print("\nDetected Tags:")
                for j, epc in enumerate(sorted(tags), 1):
                    print(f"  {j}. {epc}")
                conn.close()
                server.close()
                return

            conn.close()
            server.close()

            # Brief pause between tests
            print("   Waiting 2s for reader to reset...")
            time.sleep(2)

        except Exception as e:
            print(f"   ❌ Error: {e}")
            try:
                conn.close()
                server.close()
            except:
                pass

    print("\n" + "=" * 60)
    print("SEARCH COMPLETE")
    print(f"Best result: {best_result['tags']} tags with {best_result['config']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
