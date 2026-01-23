#!/usr/bin/env python3
"""
Get device info from M-200 with proper response parsing.
Based on successful test that returned device info.
"""

import socket
import struct
import sys
import time

HEAD = 0xCF
BROADCAST_ADDR = 0xFF
CMD_GET_DEVICE_INFO = 0x0070
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408


def calculate_crc16(data: bytes) -> int:
    crc_value = PRESET_VALUE
    for byte in data:
        crc_value ^= byte
        for _ in range(8):
            if crc_value & 0x0001:
                crc_value = (crc_value >> 1) ^ POLYNOMIAL
            else:
                crc_value = crc_value >> 1
    return crc_value


def parse_device_info(data: bytes) -> dict:
    """
    Parse device info according to manual Section 2.2.7

    Response format (152 bytes total):
    - CPHardVer: 32 Bytes (CP hardware version string)
    - CPFirmVer: 32 Bytes (CP firmware version string)
    - CPSN_code: 12 Bytes (CP serial number)
    - RFIDModeVer: 32 Bytes (RFID module hardware version)
    - RFIDModeName: 32 Bytes (RFID module name)
    - RFIDMode_SNCode: 12 Bytes (RFID module serial number)
    """
    result = {}

    if len(data) < 32:
        return {
            "error": f"Data too short: {len(data)} bytes",
            "raw": data.hex().upper(),
        }

    offset = 0

    # CPHardVer (32 bytes)
    cp_hw = data[offset : offset + 32].rstrip(b"\x00").decode("ascii", errors="replace").strip()
    result["cp_hardware_version"] = cp_hw
    offset += 32

    if len(data) >= offset + 32:
        # CPFirmVer (32 bytes)
        cp_fw = data[offset : offset + 32].rstrip(b"\x00").decode("ascii", errors="replace").strip()
        result["cp_firmware_version"] = cp_fw
        offset += 32

    if len(data) >= offset + 12:
        # CPSN_code (12 bytes)
        cp_sn = data[offset : offset + 12].rstrip(b"\x00").decode("ascii", errors="replace").strip()
        result["cp_serial_number"] = cp_sn
        offset += 12

    if len(data) >= offset + 32:
        # RFIDModeVer (32 bytes)
        rfid_hw = (
            data[offset : offset + 32].rstrip(b"\x00").decode("ascii", errors="replace").strip()
        )
        result["rfid_hardware_version"] = rfid_hw
        offset += 32

    if len(data) >= offset + 32:
        # RFIDModeName (32 bytes)
        rfid_name = (
            data[offset : offset + 32].rstrip(b"\x00").decode("ascii", errors="replace").strip()
        )
        result["rfid_module_name"] = rfid_name
        offset += 32

    if len(data) >= offset + 12:
        # RFIDMode_SNCode (12 bytes)
        rfid_sn = (
            data[offset : offset + 12].rstrip(b"\x00").decode("ascii", errors="replace").strip()
        )
        result["rfid_serial_number"] = rfid_sn
        offset += 12

    return result


def get_device_info(ip: str, port: int) -> dict:
    print("=" * 70)
    print(f"M-200 Device Info")
    print(f"Target: {ip}:{port}")
    print("=" * 70)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print(f"\nConnecting to {ip}:{port}...")
        sock.connect((ip, port))
        print("✓ Connected!")

        # Wait for device to settle
        time.sleep(0.2)

        # Build command
        frame = struct.pack(">BBHB", HEAD, BROADCAST_ADDR, CMD_GET_DEVICE_INFO, 0)
        crc = calculate_crc16(frame)
        cmd = frame + struct.pack("<H", crc)  # Little-endian CRC

        print(f"\nSending GET_DEVICE_INFO command...")
        print(f"TX: {cmd.hex().upper()}")
        sock.sendall(cmd)

        # Read response - expect 152 bytes of data + header + CRC
        sock.settimeout(5)
        print("\nWaiting for response...")

        all_data = b""
        start_time = time.time()

        while time.time() - start_time < 5:
            try:
                sock.settimeout(1)
                chunk = sock.recv(4096)
                if chunk:
                    all_data += chunk
                    print(f"Received {len(chunk)} bytes (total: {len(all_data)})")

                    # Check if we have complete frame
                    if len(all_data) >= 6 and all_data[0] == HEAD:
                        data_len = all_data[4]
                        expected_len = 5 + data_len + 2  # HEAD+ADDR+CMD+LEN + data + CRC
                        if len(all_data) >= expected_len:
                            print("Complete frame received")
                            break
                else:
                    break
            except socket.timeout:
                if all_data:
                    break
                continue

        if not all_data:
            return {"error": "No response received"}

        print(f"\nTotal received: {len(all_data)} bytes")
        print(f"RX: {all_data.hex().upper()}")

        # Parse frame
        if len(all_data) >= 6 and all_data[0] == HEAD:
            addr = all_data[1]
            cmd_resp = struct.unpack(">H", all_data[2:4])[0]
            data_len = all_data[4]
            status = all_data[5]

            print(f"\nFrame parsing:")
            print(f"  ADDR:   0x{addr:02X}")
            print(f"  CMD:    0x{cmd_resp:04X}")
            print(f"  LEN:    {data_len}")
            print(f"  STATUS: 0x{status:02X}")

            if status == 0x00:
                print("\n✓ SUCCESS!")

                # Extract data (skip status byte)
                if data_len > 1:
                    payload = all_data[6 : 6 + data_len - 1]
                    print(f"\nPayload ({len(payload)} bytes):")
                    print(f"  HEX: {payload.hex().upper()}")

                    # Parse device info
                    info = parse_device_info(payload)

                    print("\n" + "=" * 70)
                    print("DEVICE INFORMATION")
                    print("=" * 70)
                    for key, value in info.items():
                        if value:
                            print(f"  {key}: {value}")

                    return info
            else:
                status_desc = {
                    0x01: "Parameter error",
                    0x02: "Command failed",
                    0x12: "No inventory",
                    0x14: "Tag timeout",
                }.get(status, f"Unknown (0x{status:02X})")
                return {"error": f"Command failed: {status_desc}"}

        # Maybe it's in a different format - try to find ASCII strings
        print("\nAttempting ASCII extraction...")
        try:
            ascii_view = all_data.decode("ascii", errors="replace")
            # Clean up non-printable
            clean = "".join(c if c.isprintable() or c in "\n\r\t" else "|" for c in ascii_view)
            print(f"  ASCII: {clean}")
        except:
            pass

        return {"raw_response": all_data.hex().upper()}

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return {"error": str(e)}
    finally:
        sock.close()
        print("\nSocket closed")


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022

    result = get_device_info(ip, port)

    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)
    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))
