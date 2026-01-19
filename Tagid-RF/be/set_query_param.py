import socket
import struct
import time

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4001


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
    frame_body = struct.pack(
        ">BBBB", head, addr, (cmd_code >> 8) & 0xFF, cmd_code & 0xFF
    )
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

            while len(buffer) >= 6:
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
                data = frame[6:-2]

                if cmd == expected_cmd:
                    return True, status, data
                elif cmd == 0x0082:
                    continue

    except socket.timeout:
        return False, "Timeout", None
    return False, "Not Found", None


def extract_epc(payload):
    if len(payload) < 3:
        return None
    core_payload = payload[2:]
    real_len = len(core_payload)
    while real_len > 0 and core_payload[real_len - 1] == 0:
        real_len -= 1
    if real_len == 0:
        return None
    return core_payload[:real_len].hex().upper()


def main():
    print("=== SET QUERY PARAM (Multi-Tag Config) ===")
    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)

    conn, addr = server.accept()
    print(f"\n[+] Connected: {addr[0]}")

    # 1. Stop first
    print("1. Sending STOP (0x0050)...")
    conn.send(build_command(0x0050))
    success, status, _ = wait_for_response(conn, 0x0050)
    if success:
        print("   ✅ Stopped.")
    else:
        print("   ⚠️ Stop Failed.")

    time.sleep(1.0)

    # 2. Read Current Query (0x0013 with \x02)
    print("2. Reading Current Query (0x0013)...")
    conn.send(build_command(0x0013, b"\x02"))
    success, status, data = wait_for_response(conn, 0x0013)
    if success:
        print(f"   📦 Current Q Value: {data.hex().upper() if data else 'N/A'}")
    else:
        print(f"   ⚠️ Read Failed.")

    time.sleep(0.5)

    # 3. Set Query Param (0x0012)
    # Hypothesis: Prefix \x01 for SET, then Q, Session, Target
    # Q=4 (good for 16 tags), Session=0 (continuous), Target=0
    print("3. Setting Query Param (0x0012)...")
    print("   Trying: \\x01 + Q=4 + Session=0 + Target=0")

    # Format A: \x01 prefix
    payload_a = b"\x01\x04\x00\x00"
    conn.send(build_command(0x0012, payload_a))
    success, status, data = wait_for_response(conn, 0x0012)

    if success and status == 0x00:
        print(f"   ✅ SUCCESS with Format A!")
    else:
        print(f"   ❌ Format A Failed (Status: {status}). Trying Format B...")

        # Format B: No prefix, just Q, Session, Target
        payload_b = b"\x04\x00\x00"
        conn.send(build_command(0x0012, payload_b))
        success, status, data = wait_for_response(conn, 0x0012)

        if success and status == 0x00:
            print(f"   ✅ SUCCESS with Format B!")
        else:
            print(f"   ❌ Format B Failed (Status: {status}).")

    time.sleep(0.5)

    # 4. Verify New Config
    print("4. Verifying New Query Config (0x0013)...")
    conn.send(build_command(0x0013, b"\x02"))
    success, status, data = wait_for_response(conn, 0x0013)
    if success:
        print(f"   📦 New Q Value: {data.hex().upper() if data else 'N/A'}")
    else:
        print(f"   ⚠️ Verify Failed.")

    # 5. Start Inventory and Listen
    print("\n5. Starting Inventory (0x0001)...")
    conn.send(build_command(0x0001, b"\x00\x00"))

    print("\n📡 Listening for Tags (10 seconds)...")
    print("-" * 50)

    conn.settimeout(10.0)
    buffer = b""
    tags = set()
    start_time = time.time()

    try:
        while time.time() - start_time < 10:
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

                    if cmd == 0x0082 or cmd == 0x0001:
                        data = frame[5:-2]
                        if len(data) > 2:
                            epc = extract_epc(data)
                            if epc and epc not in tags:
                                tags.add(epc)
                                print(f"🏷️  NEW TAG #{len(tags)}: {epc}")
            except socket.timeout:
                break

    except KeyboardInterrupt:
        print("\nStopped.")

    print(f"\n=== Total Unique Tags: {len(tags)} ===")
    conn.close()
    server.close()


if __name__ == "__main__":
    main()
