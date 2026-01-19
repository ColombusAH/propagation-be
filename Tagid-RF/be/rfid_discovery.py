import socket
import struct
import sys
import time

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4001

# Commands to test (Command Code, Data Payload, Description)
# Complete list based on UHF Gate User Manual V1.1 (26 Commands)
COMMANDS_TO_TEST = [
    # --- 1. ISO 18000-6C Protocol ---
    (0x0003, b"\x00\x00\x00\x00", "Read Tag (RFM_READISO_TAG) - Needs Config"),
    (0x0007, b"\x00", "Set Select Mask (RFM_SETISO_SELECTMASK)"),
    (0x0010, b"\x00\x00", "Set Select Param (RFM_SET_SELPRM)"),
    (0x0011, b"", "Get Select Param (RFM_GET_SELPRM)"),
    (0x0012, b"\x01\x00\x00", "Set Query Param (RFM_SET_QUERY_PARAM)"),  # Set to defaults
    (0x0013, b"", "Get Query Param (RFM_GET_QUERY_PARAM)"),
    # --- 2. Module Custom Directives ---
    (0x0050, b"", "Init/Stop Actions (RFM_MODULE_INT)"),  # IMPORTANT for stopping!
    # (0x0052, b'', "Reboot (RFM_REBOOT) - SKIPPED FOR SAFETY"),
    (0x0053, b"\x00", "Set RF Power (RFM_SET_PWR) - Read Only Invalid"),
    (0x0059, b"\x02", "Get RF Protocol (RFM_SET_GET_RFID_PRO)"),
    (0x005F, b"\x02", "Get Net Param (RFM_SET_GET_NETPARA)"),
    (0x0064, b"\x02", "Get Remote Net Param (RFM_SET_GET_REMOTE_NETPARA)"),
    (0x0070, b"", "Get Device Info (RFM_GET_DEVICEINFO)"),
    (0x0071, b"\x00", "Set All Param (RFM_SET_ALL_PARAM) - Skipped"),
    (0x0072, b"", "Get All Params (RFM_GET_ALL_PARAM)"),
    (0x0074, b"\x02", "Get IO Param (RFM_SET_GET_IOPUT_PARAM)"),
    (0x0075, b"\x02", "Get WiFi Param (RFM_SET_GET_WiFi_PARAM)"),
    (0x0076, b"\x02", "Get Permission (RFM_SET_GET_S_PERMISSION_PARAM)"),
    (0x0077, b"\x01", "Relay 1 Control (RFM_RELEASE_CLOSE_RELAY1)"),
    (0x0078, b"\x01", "Relay 2 Control (RFM_RELEASE_CLOSE_RELAY2)"),
    (0x0079, b"\x02\x01", "Get Ant1 RSSI Filter (RFM_SET_GET_AntN_RSSI_Filter)"),
    # --- 3. GPIO Control ---
    (0x0080, b"\x02", "Get GPIO Param (RFM_SET_GET_G_PIO_WORKPARAM)"),
    (0x0081, b"", "Get GPIO Level (RFM_GET_G_PIO_LEVEL)"),
    # --- 4. Gate Access Control ---
    (0x0082, b"", "Get Gate Status (RFM_GET_GATE_STATUS) - Active Mode Source"),
    (0x0083, b"\x02", "Get Gate Param (RFM_SET_GET_GATE_PARAM)"),
    (0x0084, b"\x02", "Get EAS Mask (RFM_SET_GET_EAS_MASK)"),
]


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


def drain_socket(client, duration=0.5):
    """Read and discard all data from socket for a duration."""
    end_time = time.time() + duration
    client.settimeout(0.1)
    bytes_read = 0
    try:
        while time.time() < end_time:
            chunk = client.recv(4096)
            if not chunk:
                break
            bytes_read += len(chunk)
    except socket.timeout:
        pass
    # print(f"  [i] Drained {bytes_read} bytes of noise.")
    client.settimeout(2.0)  # Restore timeout


def wait_for_response(client, expected_cmd):
    """Loop read until specific CMD response is found."""
    start_time = time.time()
    buffer = b""
    while time.time() - start_time < 3.0:  # 3s Timeout
        try:
            chunk = client.recv(4096)
            if not chunk:
                return False, "Connection Closed"
            buffer += chunk

            while len(buffer) >= 6:
                if buffer[0] != 0xCF:
                    # Scan ahead for header
                    idx = buffer.find(b"\xcf", 1)
                    if idx != -1:
                        buffer = buffer[idx:]
                    else:
                        buffer = b""
                    continue

                length = buffer[4]
                if len(buffer) < 7 + length:
                    break

                # Extract Frame
                frame = buffer[: 7 + length]
                buffer = buffer[7 + length :]

                cmd = (frame[2] << 8) | frame[3]
                status = frame[5]

                if cmd == expected_cmd:
                    return True, status
                elif cmd == 0x0082:
                    continue  # Ignore tag reports
                elif cmd == 0x0001 and expected_cmd == 0x0001:
                    return True, status  # Special case for Inventory
                else:
                    # print(f"  [i] Ignored unsolicited CMD: 0x{cmd:04X}")
                    pass

        except socket.timeout:
            return False, "Timeout"

    return False, "Timeout Loop"


def run_discovery():
    print(f"=== RFID COMMAND DISCOVERY (ACTIVE MODE COMPATIBLE) ===")
    print(f"1. Listening on {LISTEN_IP}:{LISTEN_PORT}...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((LISTEN_IP, LISTEN_PORT))
        server.listen(1)
        print("Waiting for Reader to connect...")

        client, addr = server.accept()
        print(f"\n[+] Reader Connected! IP: {addr[0]}")

        target_addr = 0xFF  # Use Broadcast for discovery

        print(f"\n[Step 2] Testing {len(COMMANDS_TO_TEST)} Commands...")

        for cmd_code, payload, desc in COMMANDS_TO_TEST:
            print(f"\n--- Testing: {desc} (0x{cmd_code:04X}) ---")

            # Drain before sending
            drain_socket(client, duration=0.2)

            # Send
            request = build_command(cmd_code, data=payload, addr=target_addr)
            # print(f"[TX] {request.hex().upper()}")
            client.send(request)

            # Wait for specific response
            success, status = wait_for_response(client, cmd_code)

            if success:
                print(f"  [+] RESPONSE RECEIVED! Status: 0x{status:02X}")
                if status == 0x00:
                    print(f"      ✅ Command Supported & Successful")
                else:
                    print(f"      ⚠️  Command Supported but Failed (Error)")
            else:
                print(f"  [-] NO RESPONSE ({status})")

            time.sleep(0.2)

    except Exception as e:
        print(f"[!] Server Error: {e}")
    finally:
        server.close()
        print("\n=== Discovery Complete ===")


if __name__ == "__main__":
    run_discovery()
