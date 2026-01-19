import socket
import struct
import sys
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


def build_command(cmd_code: int, data: bytes = b"", addr: int = 0x01) -> bytes:
    head = 0xCF
    frame_body = struct.pack(
        ">BBBB", head, addr, (cmd_code >> 8) & 0xFF, cmd_code & 0xFF
    )
    frame_body += struct.pack("B", len(data))
    frame_body += data
    crc = calculate_crc16(frame_body)
    # FIXED: Big Endian CRC (>H)
    return frame_body + struct.pack(">H", crc)


def run_test():
    print(f"=== RFID SINGLE-SOCKET VERIFICATION ===")
    print(f"1. Listening on {LISTEN_IP}:{LISTEN_PORT}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((LISTEN_IP, LISTEN_PORT))
        server.listen(1)
        print("Waiting for Reader to connect...")

        client, addr = server.accept()
        print(f"\n[+] Reader Connected! IP: {addr[0]}")

        # Give it a moment to settle
        time.sleep(1.0)

        # 0. Probe with GET DEVICE INFO (0x0070) - Broadcast
        print("\n[>] Sending GET DEVICE INFO (0x0070) to Addr 0xFF...")
        cmd_info = build_command(0x0070, data=b"", addr=0xFF)  # Broadcast
        print(f"[TX] {cmd_info.hex().upper()}")
        client.send(cmd_info)

        target_addr = 0xFF  # Fallback

        # Wait specifically for info response
        client.settimeout(2.0)
        try:
            resp = client.recv(1024)
            print(f"[RX-Info] {len(resp)} bytes: {resp.hex().upper()}")

            # Extract Address
            # Frame: CF [ADDR] ...
            if len(resp) > 1 and resp[0] == 0xCF:
                target_addr = resp[1]
                print(f"[!] Detected Reader Address: 0x{target_addr:02X}")

        except socket.timeout:
            print("[!] No response to GET INFO. Using Addr 0x01...")
            target_addr = 0x01
        except Exception as e:
            print(f"[!] Info probe error: {e}")

        client.settimeout(None)  # Reset timeout

        # 0.5 Send STOP INVENTORY first (to clear state)
        print(f"\n[>] Sending STOP INVENTORY (0x0028) to Addr 0x{target_addr:02X}...")
        cmd_stop = build_command(0x0028, data=b"", addr=target_addr)
        print(f"[TX] {cmd_stop.hex().upper()}")
        client.send(cmd_stop)
        time.sleep(0.5)

        # 1. Send Inventory Command (Corrected)
        # Addr: Detected Address
        # Payload: b'\x00\x00' (Type=0, Param=0 -> Continuous)
        print(f"\n[>] Sending START INVENTORY (0x0001) to Addr 0x{target_addr:02X}...")
        cmd = build_command(0x0001, data=b"\x00\x00", addr=target_addr)
        print(f"[TX] {cmd.hex().upper()}")
        client.send(cmd)

        # 2. Read Loop
        print("\n[<] Listening for Tags... (Press Ctrl+C to stop)")
        tag_counts = {}
        total_packets = 0

        while True:
            data = client.recv(4096)
            if not data:
                print("[-] Reader Disconnected.")
                break

            # Hex dump - VERBOSE per User Request
            print(f"[RX] {data.hex().upper()}")
            total_packets += 1

            # Simple Parsing of 0x0001 Response
            # Frame: CF Addr CmdH CmdL Len [Status RSSI Ant ... EPC ...] CRC

            i = 0
            while i < len(data):
                if data[i] == 0xCF:
                    # Potential start
                    if i + 5 < len(data):
                        length = data[i + 4]
                        if i + 5 + length + 2 <= len(data):
                            # Full frame
                            frame = data[i : i + 5 + length + 2]
                            cmd = (frame[2] << 8) | frame[3]  # Big Endian CMD

                            print(
                                f"[!] Frame Detected. CMD: 0x{cmd:04X} | Len: {length}"
                            )

                            # Accept 0x0001 (Inventory), 0x0018 (Cached), or 0x0082 (Auto-Report)
                            if cmd in [0x0001, 0x0018, 0x0082]:
                                payload = frame[5:-2]  # Remove Head..Len and CRC
                                if len(payload) > 3:
                                    status = payload[0]

                                    # 0x0082 often has no status byte, just data?
                                    # Or Status is byte 0?
                                    # Logs showed: CF 01 00 82 26 01 00 00 ...
                                    # Len=0x26 (38). Payload starts at byte 5 (Len).
                                    # Byte 6 is Status? 01?
                                    # If 0x0082, structure might be different.
                                    # Let's just print the raw hex of the tag data for now.

                                    # Heuristic: Find EPC (starts usually after RSSI/Ant)
                                    # M-200 0x0082 format: [Ant][RSSI][PC][EPC...] ?
                                    # Let's just treat payload as "Data"

                                    if len(payload) > 1:
                                        raw_payload = payload.hex().upper()
                                        print(f"[!] TAG DATA: {raw_payload}")

                                        # Count it
                                        tag_counts[raw_payload] = (
                                            tag_counts.get(raw_payload, 0) + 1
                                        )

                            i += 5 + length + 2
                            continue
                i += 1

    except OSError as e:
        print(f"\n[!] Error: {e}")
        print("    (Did you stop the other server? Port 4001 must be free.)")
    except KeyboardInterrupt:
        print("\n\nTest Stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    run_test()
