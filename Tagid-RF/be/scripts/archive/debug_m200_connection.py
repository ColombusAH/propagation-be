#!/usr/bin/env python3
"""
Debug script to test raw M-200 communication.
Tests the protocol implementation with detailed logging.
"""

import socket
import struct
import sys

# M-200 Protocol constants
HEAD = 0xCF
BROADCAST_ADDR = 0xFF
CMD_GET_DEVICE_INFO = 0x0021
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408


def calculate_crc16(data: bytes) -> int:
    """Calculate CRC16 checksum"""
    crc_value = PRESET_VALUE
    for byte in data:
        crc_value ^= byte
        for _ in range(8):
            if crc_value & 0x0001:
                crc_value = (crc_value >> 1) ^ POLYNOMIAL
            else:
                crc_value = crc_value >> 1
    return crc_value


def build_get_device_info_command() -> bytes:
    """Build RFM_GET_DEVICE_INFO command according to manual"""
    # Frame format: [HEAD][ADDR][CMD_H][CMD_L][LEN][DATA][CRC_L][CRC_H]
    frame = struct.pack(">BBHB", HEAD, BROADCAST_ADDR, CMD_GET_DEVICE_INFO, 0)
    # frame is now: [CF][FF][00 21][00]

    # Calculate CRC
    crc = calculate_crc16(frame)

    # Append CRC (little-endian)
    frame += struct.pack("<H", crc)

    return frame


def test_m200_connection(ip: str, port: int, timeout: int = 10):
    """Test M-200 connection with detailed debugging"""

    print("=" * 70)
    print(f"M-200 Connection Debug Test")
    print(f"Target: {ip}:{port}")
    print(f"Timeout: {timeout}s")
    print("=" * 70)

    # Step 1: Create socket
    print("\n[Step 1] Creating TCP socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    print("✓ Socket created")

    try:
        # Step 2: Connect
        print(f"\n[Step 2] Connecting to {ip}:{port}...")
        sock.connect((ip, port))
        print(f"✓ TCP connection established to {ip}:{port}")

        # Step 3: Build command
        print("\n[Step 3] Building RFM_GET_DEVICE_INFO command...")
        cmd = build_get_device_info_command()
        print(f"Command bytes ({len(cmd)} bytes):")
        print(f"  HEX: {cmd.hex().upper()}")
        print(f"  Breakdown:")
        print(f"    HEAD:     0x{cmd[0]:02X} (should be 0xCF)")
        print(f"    ADDR:     0x{cmd[1]:02X} (0xFF = broadcast)")
        print(f"    CMD:      0x{cmd[2]:02X}{cmd[3]:02X} (0x0021 = GET_DEVICE_INFO)")
        print(f"    LEN:      0x{cmd[4]:02X} (0 = no data)")
        print(f"    CRC:      0x{cmd[5]:02X}{cmd[6]:02X}")

        # Step 4: Send command
        print("\n[Step 4] Sending command...")
        bytes_sent = sock.sendall(cmd)
        print(f"✓ Sent {len(cmd)} bytes")

        # Step 5: Wait for response
        print(f"\n[Step 5] Waiting for response (timeout: {timeout}s)...")
        print("Expecting response format: [HEAD][ADDR][CMD_H][CMD_L][LEN][STATUS][DATA...][CRC]")

        # Try to receive header (6 bytes minimum)
        print("\n  Reading header (6 bytes)...")
        header = b""
        try:
            while len(header) < 6:
                chunk = sock.recv(6 - len(header))
                if not chunk:
                    print("  ✗ Connection closed by remote host")
                    return False
                header += chunk
                print(f"  Received {len(chunk)} bytes, total: {len(header)}/6")

            print(f"\n  ✓ Header received:")
            print(f"    HEX: {header.hex().upper()}")
            print(f"    HEAD:     0x{header[0]:02X}")
            print(f"    ADDR:     0x{header[1]:02X}")
            print(f"    CMD:      0x{header[2]:02X}{header[3]:02X}")
            print(f"    LEN:      0x{header[4]:02X} ({header[4]} bytes of data)")
            print(f"    STATUS:   0x{header[5]:02X}")

            # Get data length
            data_len = header[4]

            # Receive remaining data + CRC
            print(f"\n  Reading data + CRC ({data_len + 2} bytes)...")
            remaining = b""
            bytes_to_read = data_len + 2
            while len(remaining) < bytes_to_read:
                chunk = sock.recv(bytes_to_read - len(remaining))
                if not chunk:
                    print("  ✗ Connection closed before receiving all data")
                    return False
                remaining += chunk
                print(f"  Received {len(chunk)} bytes, total: {len(remaining)}/{bytes_to_read}")

            full_response = header + remaining
            print(f"\n  ✓ Complete response received ({len(full_response)} bytes):")
            print(f"    HEX: {full_response.hex().upper()}")

            # Parse response
            if header[5] == 0x00:
                print(f"\n  ✓ STATUS: 0x00 (Success)")

                # Parse device info if we have data
                if data_len >= 24:
                    data = remaining[:data_len]
                    cp_hw = f"{data[0]}.{data[1]}"
                    cp_fw = f"{data[2]}.{data[3]}"
                    rfid_hw = f"{data[4]}.{data[5]}"
                    rfid_fw = f"{data[6]}.{data[7]}"
                    serial = data[8:24].hex().upper()

                    print(f"\n  Device Information:")
                    print(f"    CP Hardware:    {cp_hw}")
                    print(f"    CP Firmware:    {cp_fw}")
                    print(f"    RFID Hardware:  {rfid_hw}")
                    print(f"    RFID Firmware:  {rfid_fw}")
                    print(f"    Serial Number:  {serial}")
            else:
                print(f"\n  ✗ STATUS: 0x{header[5]:02X} (Error)")
                status_desc = {
                    0x01: "Parameter error",
                    0x02: "Command failed",
                    0x03: "Reserved",
                    0x12: "No inventory/completed",
                    0x14: "Tag timeout",
                }.get(header[5], "Unknown error")
                print(f"    Description: {status_desc}")

            # Verify CRC
            crc_received = struct.unpack("<H", full_response[-2:])[0]
            crc_calculated = calculate_crc16(full_response[:-2])
            print(f"\n  CRC Check:")
            print(f"    Received:   0x{crc_received:04X}")
            print(f"    Calculated: 0x{crc_calculated:04X}")
            if crc_received == crc_calculated:
                print(f"    ✓ CRC valid")
            else:
                print(f"    ✗ CRC mismatch!")

            print("\n" + "=" * 70)
            print("✓ Test PASSED - M-200 communication working!")
            print("=" * 70)
            return True

        except socket.timeout:
            print(f"\n  ✗ TIMEOUT after {timeout}s waiting for response")
            print("\n  Possible causes:")
            print("    1. M-200 is not responding to commands on this port")
            print("    2. Wrong port (try 4001, 6000, 27011)")
            print("    3. M-200 might use different protocol/firmware")
            print("    4. Network issues or firewall blocking")
            return False

    except socket.timeout:
        print(f"\n✗ Connection timeout after {timeout}s")
        print("\nPossible causes:")
        print("  1. M-200 is not accessible at this IP:port")
        print("  2. Firewall blocking connection")
        print("  3. Wrong IP address")
        return False

    except ConnectionRefusedError:
        print(f"\n✗ Connection refused by {ip}:{port}")
        print("\nPossible causes:")
        print("  1. M-200 TCP server not enabled")
        print("  2. Wrong port number")
        print("  3. M-200 in wrong operating mode")
        return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        sock.close()
        print("\nSocket closed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Debug M-200 RFID reader connection")
    parser.add_argument("--ip", default="169.254.128.161", help="M-200 IP address")
    parser.add_argument("--port", type=int, default=5000, help="M-200 port")
    parser.add_argument("--timeout", type=int, default=10, help="Socket timeout in seconds")

    args = parser.parse_args()

    success = test_m200_connection(args.ip, args.port, args.timeout)
    sys.exit(0 if success else 1)
