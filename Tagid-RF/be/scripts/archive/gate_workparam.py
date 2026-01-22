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
    print("=== GATE WORKPARAM (0x0083) - Section 2.5.2 ===")
    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)

    conn, addr = server.accept()
    print(f"\n[+] Connected: {addr[0]}")

    # 1. Stop first
    print("\n1. Sending STOP (0x0050)...")
    conn.send(build_command(0x0050))
    success, status, _ = wait_for_response(conn, 0x0050)
    if success:
        print("   ✅ Stopped.")
    else:
        print("   ⚠️ Stop Failed (continuing anyway).")

    time.sleep(1.0)

    # 2. Read Gate WorkParam (0x0083 with Option=0x02 for read)
    print("\n2. Reading Gate WorkParam (0x0083)...")
    conn.send(build_command(0x0083, b"\x02"))
    success, status, data = wait_for_response(conn, 0x0083)

    if success and data:
        print(f"   ✅ SUCCESS! Status: {status}")
        print(f"   📦 Raw Data ({len(data)} bytes): {data.hex().upper()}")

        # Parse based on manual Section 2.5.2
        # GATEMODE, GATEGPI1, GATEGPI2, POWER_GPO, READING_GPO, RECV_GPIO(4), EAS_MODE, EAS_GPO, RECV_FUNC(6)
        if len(data) >= 1:
            gatemode = data[0]
            gatemode_names = {
                0: "Inventory Mode (counting)",
                1: "EAS Mode (entry/exit)",
            }
            print(f"\n   📊 GATEMODE: 0x{gatemode:02X} - {gatemode_names.get(gatemode, 'Unknown')}")

        if len(data) >= 2:
            print(f"   📊 GATEGPI1: 0x{data[1]:02X}")
        if len(data) >= 3:
            print(f"   📊 GATEGPI2: 0x{data[2]:02X}")
        if len(data) >= 4:
            print(f"   📊 POWER_GPO: 0x{data[3]:02X}")
        if len(data) >= 5:
            print(f"   📊 READING_GPO: 0x{data[4]:02X}")
        if len(data) >= 9:
            print(f"   📊 RECV_GPIO: {data[5:9].hex().upper()}")
        if len(data) >= 10:
            eas_mode = data[9]
            print(f"   📊 EAS_MODE: 0x{eas_mode:02X}")
        if len(data) >= 11:
            print(f"   📊 EAS_GPO: 0x{data[10]:02X}")
        if len(data) >= 17:
            print(f"   📊 RECV_FUNC: {data[11:17].hex().upper()}")
    else:
        print(f"   ❌ Failed (Status: {status})")
        conn.close()
        server.close()
        return

    time.sleep(0.5)

    # 3. Set to Inventory Mode (0x00) for continuous counting
    print("\n" + "=" * 50)
    print("Setting GATEMODE to 0x00 (Inventory Mode)")
    print("This should enable continuous tag counting.")
    print("=" * 50)

    # Build payload: Option(0x01) + GATEMODE(0x00) + rest of params
    # Payload is 18 bytes total based on manual
    # We'll use the current data but change GATEMODE to 0x00
    if len(data) >= 17:
        new_data = bytearray(data)
        new_data[0] = 0x00  # GATEMODE = Inventory Mode
        set_payload = b"\x01" + bytes(new_data)  # Option=0x01 (set) + data
    else:
        # Default payload if we don't have full data
        set_payload = b"\x01"  # Option = Set
        set_payload += b"\x00"  # GATEMODE = Inventory Mode
        set_payload += b"\x00" * 16  # Remaining bytes as zeros

    print(f"\n3. Setting Gate WorkParam (0x0083)...")
    print(f"   Payload ({len(set_payload)} bytes): {set_payload.hex().upper()}")

    conn.send(build_command(0x0083, set_payload))
    success, status, response = wait_for_response(conn, 0x0083)

    if success and status == 0x00:
        print("   ✅ SUCCESS! GATEMODE set to Inventory Mode.")
    else:
        print(f"   ❌ Failed (Status: {status})")

    time.sleep(0.5)

    # 4. Verify
    print("\n4. Verifying Gate WorkParam...")
    conn.send(build_command(0x0083, b"\x02"))
    success, status, data = wait_for_response(conn, 0x0083)

    if success and data:
        print(f"   📦 New Data: {data.hex().upper()}")
        if len(data) >= 1:
            gatemode = data[0]
            gatemode_names = {0: "Inventory Mode", 1: "EAS Mode"}
            print(f"   📊 GATEMODE: 0x{gatemode:02X} - {gatemode_names.get(gatemode, 'Unknown')}")
    else:
        print("   ⚠️ Verify Failed.")

    print("\n5. Power cycle the reader and run passive_listener.py to test!")

    conn.close()
    server.close()


if __name__ == "__main__":
    main()
