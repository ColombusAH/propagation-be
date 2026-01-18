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
    print("=== SET ALL PARAMS (Change WorkMode to Active) ===")
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
        print("   ⚠️ Stop Failed.")

    time.sleep(1.0)

    # 2. Read Current Params (0x0072)
    print("\n2. Reading Current Params (0x0072)...")
    conn.send(build_command(0x0072))
    success, status, data = wait_for_response(conn, 0x0072)

    if success and data:
        print(f"   ✅ Current Data ({len(data)} bytes): {data.hex().upper()}")

        # Parse key values
        if len(data) >= 19:
            work_mode = data[2]
            q_value = data[17] if len(data) > 17 else "?"
            session = data[18] if len(data) > 18 else "?"

            work_modes = {0: "Answer Mode", 1: "Active Mode", 2: "Trigger Mode"}
            print(f"   📊 Current WorkMode: {work_mode} ({work_modes.get(work_mode, 'Unknown')})")
            print(f"   📊 Current QValue: {q_value}")
            print(f"   📊 Current Session: {session}")
    else:
        print(f"   ❌ Read Failed (Status: {status})")
        conn.close()
        server.close()
        return

    time.sleep(0.5)

    # 3. Set New Params (0x0071)
    # Change WorkMode from 02 to 01 (Active Mode)
    # Also set QValue to 04 and Session to 00
    print("\n3. Setting New Params (0x0071)...")

    # Create new payload - change byte 2 from 02 to 01 (WorkMode = Active)
    # Original: 0100022000000101038602EE01F43121010400000C03030100
    # Modified: 0100012000000101038602EE01F43121010400000C03030100
    #                 ^ WorkMode changed from 02 to 01

    # Build new params based on current, changing WorkMode to 1
    new_params = bytearray(data)
    new_params[2] = 0x01  # WorkMode = Active Mode

    # Ensure Q and Session are good
    if len(new_params) > 17:
        new_params[17] = 0x04  # QValue = 4
    if len(new_params) > 18:
        new_params[18] = 0x00  # Session = 0

    print(f"   📝 New Data: {bytes(new_params).hex().upper()}")
    print(f"   🔧 WorkMode: 0x01 (Active Mode)")
    print(f"   🔧 QValue: 0x04")
    print(f"   🔧 Session: 0x00")

    conn.send(build_command(0x0071, bytes(new_params)))
    success, status, data = wait_for_response(conn, 0x0071)

    if success and status == 0x00:
        print(f"   ✅ SUCCESS! Params Updated.")
    else:
        print(f"   ❌ Failed (Status: {status})")

    time.sleep(0.5)

    # 4. Verify New Params
    print("\n4. Verifying New Params (0x0072)...")
    conn.send(build_command(0x0072))
    success, status, data = wait_for_response(conn, 0x0072)

    if success and data:
        print(f"   📦 New Data: {data.hex().upper()}")
        if len(data) >= 19:
            work_mode = data[2]
            q_value = data[17]
            session = data[18]

            work_modes = {0: "Answer Mode", 1: "Active Mode", 2: "Trigger Mode"}
            print(f"   📊 WorkMode: {work_mode} ({work_modes.get(work_mode, 'Unknown')})")
            print(f"   📊 QValue: {q_value}")
            print(f"   📊 Session: {session}")

            if work_mode == 1:
                print("\n   🎉 SUCCESS! Reader is now in ACTIVE MODE!")
    else:
        print(f"   ⚠️ Verify Failed.")

    print("\n5. Power cycle the reader and run proper_inventory.py to test!")

    conn.close()
    server.close()


if __name__ == "__main__":
    main()
