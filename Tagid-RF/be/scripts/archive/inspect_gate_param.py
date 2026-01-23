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


def main():
    print("=== INSPECT GATE PARAM (0x0083) ===")
    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)

    conn, addr = server.accept()
    print(f"\n[+] Connected: {addr[0]}")

    # 1. Stop first (System Command)
    print("1. Sending STOP (0x0050)...")
    conn.send(build_command(0x0050))
    success, status, _ = wait_for_response(conn, 0x0050)
    if success:
        print("   ✅ Stopped.")
    else:
        print("   ⚠️ Stop Failed.")

    time.sleep(1.0)

    # 2. Get Gate Param (0x0083)
    print("2. Getting Gate Param (0x0083) with payload \\x02...")
    conn.send(build_command(0x0083, b"\x02"))
    success, status, data = wait_for_response(conn, 0x0083)

    if success:
        print(f"   ✅ SUCCESS! Status: {status}")
        if data:
            print(f"   📦 Data (Hex): {data.hex().upper()}")
    else:
        print(f"   ❌ Failed (Status: {status})")

    time.sleep(1.0)

    # 3. Get Query Param (0x0013) - Try with Payload \x02?
    print("3. Getting Query Param (0x0013) with payload \\x02...")
    conn.send(build_command(0x0013, b"\x02"))
    success, status, data = wait_for_response(conn, 0x0013)

    if success:
        print(f"   ✅ QUERY READ SUCCESS! Status: {status}")
        if data:
            print(f"   📦 Query Data: {data.hex().upper()}")
    else:
        print(f"   ❌ Failed (Status: {status})")

    conn.close()
    server.close()


if __name__ == "__main__":
    main()
