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


def main():
    print("=== GPIO PARAMETERS (0x0080) ===")
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

    # 2. Read GPIO Params (0x0080 with option=0x02 for read)
    print("\n2. Reading GPIO Params (0x0080)...")
    conn.send(build_command(0x0080, b"\x02"))
    success, status, data = wait_for_response(conn, 0x0080)

    if success and data:
        print(f"   ✅ SUCCESS! Status: {status}")
        print(f"   📦 Raw Data ({len(data)} bytes): {data.hex().upper()}")

        # Parse based on manual Section 2.4.1
        # GPIOMODE, GPIEN, INTLEVEL, GPOEN, PUTLEVEL, PUTTIME(8 bytes)
        if len(data) >= 5:
            gpiomode = data[0]
            gpien = data[1] if len(data) > 1 else 0
            intlevel = data[2] if len(data) > 2 else 0
            gpoen = data[3] if len(data) > 3 else 0
            putlevel = data[4] if len(data) > 4 else 0

            mode_names = {
                0: "General Mode (GPIO triggers reading)",
                1: "Door Access Mode (gate settings)",
            }
            print(
                f"\n   📊 GPIOMODE: 0x{gpiomode:02X} - {mode_names.get(gpiomode, 'Unknown')}"
            )
            print(f"   📊 GPIEN:    0x{gpien:02X}")
            print(f"   📊 INTLEVEL: 0x{intlevel:02X}")
            print(f"   📊 GPOEN:    0x{gpoen:02X}")
            print(f"   📊 PUTLEVEL: 0x{putlevel:02X}")

            if len(data) > 5:
                puttime = data[5:13] if len(data) >= 13 else data[5:]
                print(f"   📊 PUTTIME:  {puttime.hex().upper()}")
    else:
        print(f"   ❌ Failed (Status: {status})")
        conn.close()
        server.close()
        return

    time.sleep(0.5)

    # 3. Ask user if they want to change to Door Access Mode
    print("\n" + "=" * 50)
    print("If GPIOMODE is 0x00 (General), changing to 0x01 (Door Access)")
    print("might enable continuous gate detection without GPIO trigger.")
    print("=" * 50)

    # 4. Set GPIO to Door Access Mode (0x01)
    print("\n3. Setting GPIO to Door Access Mode (0x0080)...")
    # Based on manual: Option=0x01 for set, then GPIOMODE, GPIEN, INTLEVEL, GPOEN, PUTLEVEL, PUTTIME
    # Set GPIOMODE=0x01 (Door Access), keep other values
    set_payload = b"\x01"  # Option = Set
    set_payload += b"\x01"  # GPIOMODE = Door Access Mode
    set_payload += b"\x00"  # GPIEN
    set_payload += b"\x00"  # INTLEVEL
    set_payload += b"\x01"  # GPOEN
    set_payload += b"\x00"  # PUTLEVEL
    set_payload += (
        b"\xff\x00\x00\x00\x00\x00\x00\x00"  # PUTTIME (8 bytes, 0xFF = continuous)
    )

    print(f"   Payload: {set_payload.hex().upper()}")
    conn.send(build_command(0x0080, set_payload))
    success, status, data = wait_for_response(conn, 0x0080)

    if success and status == 0x00:
        print("   ✅ SUCCESS! GPIO set to Door Access Mode.")
    else:
        print(f"   ❌ Failed (Status: {status})")

    time.sleep(0.5)

    # 5. Verify
    print("\n4. Verifying GPIO Params...")
    conn.send(build_command(0x0080, b"\x02"))
    success, status, data = wait_for_response(conn, 0x0080)

    if success and data:
        print(f"   📦 New Data: {data.hex().upper()}")
        if len(data) >= 1:
            gpiomode = data[0]
            mode_names = {0: "General Mode", 1: "Door Access Mode"}
            print(
                f"   📊 GPIOMODE: 0x{gpiomode:02X} - {mode_names.get(gpiomode, 'Unknown')}"
            )

    print("\n5. Power cycle the reader and test again!")

    conn.close()
    server.close()


if __name__ == "__main__":
    main()
