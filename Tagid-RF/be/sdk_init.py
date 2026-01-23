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


def drain_and_wait(conn, cmd, timeout=3.0):
    """Drain incoming data and wait for specific command response"""
    conn.settimeout(timeout)
    buffer = b""
    start = time.time()
    try:
        while time.time() - start < timeout:
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

                frame_cmd = (frame[2] << 8) | frame[3]
                if frame_cmd == cmd:
                    return True, frame[5], frame[6:-2]
    except socket.timeout:
        pass
    return False, None, None


def main():
    print("=" * 60)
    print("SDK-BASED INITIALIZATION")
    print("Will configure reader properly before scanning")
    print("=" * 60)
    print(f"\nListening on {LISTEN_IP}:{LISTEN_PORT}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)

    print("Waiting for reader connection (power cycle if needed)...")
    conn, addr = server.accept()
    print(f"[+] Connected: {addr[0]}:{addr[1]}")

    # Drain any initial data
    print("\n1. Draining initial data...")
    time.sleep(1)
    conn.settimeout(0.5)
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            print(f"   Drained: {len(data)} bytes")
    except socket.timeout:
        pass
    print("   Done draining")

    # 2. Get Device Info (0x0070)
    print("\n2. Getting Device Info (0x0070)...")
    conn.send(build_command(0x0070))
    success, status, data = drain_and_wait(conn, 0x0070)
    if success:
        print(f"   ✅ Status: {status}, Data: {data.hex().upper()[:40] if data else 'None'}...")
    else:
        print("   ⚠️ No response")

    # 3. Get Device Parameters (0x0072)
    print("\n3. Getting Device Parameters (0x0072)...")
    conn.send(build_command(0x0072))
    success, status, data = drain_and_wait(conn, 0x0072)
    if success and data:
        print(f"   ✅ Status: {status}")
        print(f"   📦 Data ({len(data)} bytes): {data.hex().upper()}")
        if len(data) >= 3:
            workmode = data[2]
            modes = {0: "Answer", 1: "Active", 2: "Trigger"}
            print(f"   📊 Current WORKMODE: {workmode} ({modes.get(workmode, '?')})")
        if len(data) >= 18:
            print(f"   📊 QVALUE: {data[17]}")
        if len(data) >= 19:
            print(f"   📊 SESSION: {data[18]}")
    else:
        print("   ⚠️ No response - reader may need different command format")

    # 4. Try to set WORKMODE to Active (1)
    print("\n4. Setting WORKMODE to Active (0x0071)...")
    if success and data and len(data) >= 20:
        new_params = bytearray(data)
        new_params[2] = 0x01  # WORKMODE = Active
        if len(new_params) > 17:
            new_params[17] = 0x05  # QVALUE = 5
        if len(new_params) > 18:
            new_params[18] = 0x00  # SESSION = 0

        conn.send(build_command(0x0071, bytes(new_params)))
        success, status, _ = drain_and_wait(conn, 0x0071)
        if success and status == 0x00:
            print("   ✅ WORKMODE set to Active!")
        else:
            print(f"   ⚠️ Status: {status}")
    else:
        # Try with minimal params
        print("   Trying minimal SetDevicePara...")
        # Based on SDK structure
        params = bytes(
            [
                0x01,  # DEVICEADDR
                0x00,  # RFIDPRO
                0x01,  # WORKMODE = Active
                0x20,  # INTERFACE
                0x04,  # BAUDRATE
                0x00,  # WGSET
                0x01,  # ANT
                0x08,  # REGION (China Band 2)
            ]
        )
        conn.send(build_command(0x0071, params))
        success, status, _ = drain_and_wait(conn, 0x0071)
        print(f"   Result: {'✅' if success and status == 0x00 else '⚠️'}")

    time.sleep(0.5)

    # 5. Start Continuous Inventory
    print("\n5. Starting Continuous Inventory (0x0001)...")
    # invCount=0x00 (by time), invParam=0 (continuous)
    inv_payload = b"\x00\x00\x00\x00\x00"
    conn.send(build_command(0x0001, inv_payload))

    print("\n📡 Listening for Tags (60 seconds)...")
    print("   MOVE TAGS THROUGH THE GATE NOW!")
    print("-" * 60)

    conn.settimeout(1.0)
    buffer = b""
    tags = {}
    frame_count = 0
    start_time = time.time()

    try:
        while time.time() - start_time < 60:
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

                    frame_count += 1

                    # Look for EPCs in any frame
                    # Common EPC prefixes
                    for prefix in [b"\xe2\x80", b"\xe2\x00", b"\x30\x00"]:
                        idx = payload.find(prefix)
                        if idx != -1 and idx + 12 <= len(payload):
                            epc = payload[idx : idx + 12].hex().upper()
                            if epc not in tags:
                                tags[epc] = 0
                                print(f"🆕 TAG #{len(tags)}: {epc}")
                                print(f"   From CMD: 0x{cmd:04X}, Status: 0x{status:02X}")
                            tags[epc] += 1
                            break

                    # Also check status 0x00 for inventory response
                    if status == 0x00 and cmd == 0x0001 and len(payload) >= 12:
                        # Try to extract EPC from standard position
                        if len(payload) >= 9:
                            epc_len = payload[8] if len(payload) > 8 else 0
                            if 4 <= epc_len <= 24 and len(payload) >= 9 + epc_len:
                                epc = payload[9 : 9 + epc_len].hex().upper()
                                if epc not in tags:
                                    tags[epc] = 0
                                    print(f"🆕 INV TAG #{len(tags)}: {epc}")
                                tags[epc] += 1

            except socket.timeout:
                continue
    except KeyboardInterrupt:
        pass

    # Stop inventory
    print("\n6. Stopping...")
    conn.send(build_command(0x0050))

    print("-" * 60)
    print(f"\n=== SUMMARY ===")
    print(f"Total Frames: {frame_count}")
    print(f"Unique Tags: {len(tags)}")
    for i, (epc, count) in enumerate(sorted(tags.items(), key=lambda x: -x[1]), 1):
        print(f"  {i}. {epc} (seen {count}x)")

    conn.close()
    server.close()


if __name__ == "__main__":
    main()
