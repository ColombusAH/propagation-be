#!/usr/bin/env python3
"""
Simple test script to get device info from M-200 using both command codes.
"""

import socket
import struct
import sys

# M-200 Protocol constants
HEAD = 0xCF
BROADCAST_ADDR = 0xFF
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408

# Command codes to try
COMMANDS = {
    0x0070: "RFM_GET_DEVICE_INFO (from manual Section 2.2.7)",
    0x0021: "Get Device Info (alternate)",
    0x0072: "RFM_MODULE_INT (Initialize)",
    0x0052: "RFM_GET_ALL_PARAM (Get all parameters)",
}


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


def build_command(cmd: int, data: bytes = b"") -> bytes:
    """Build M-200 command frame"""
    frame = struct.pack(">BBHB", HEAD, BROADCAST_ADDR, cmd, len(data)) + data
    # Try both little-endian and big-endian CRC
    crc = calculate_crc16(frame)
    # Use little-endian CRC (as in debug script)
    frame_le = frame + struct.pack("<H", crc)
    return frame_le


def try_command(sock: socket.socket, cmd: int, desc: str, timeout: float = 3.0) -> bool:
    """Try sending a command and getting response"""
    print(f"\n--- Trying CMD 0x{cmd:04X}: {desc} ---")

    cmd_bytes = build_command(cmd)
    print(f"  TX: {cmd_bytes.hex().upper()}")

    sock.settimeout(timeout)
    sock.sendall(cmd_bytes)

    # Try to receive response
    try:
        # First try to read any data with short timeout
        sock.settimeout(timeout)
        response = sock.recv(1024)

        if response:
            print(f"  RX: {response.hex().upper()} ({len(response)} bytes)")

            # Try to parse header
            if len(response) >= 6 and response[0] == HEAD:
                addr = response[1]
                resp_cmd = struct.unpack(">H", response[2:4])[0]
                data_len = response[4]
                status = response[5]
                print(f"  Parsed:")
                print(f"    ADDR:   0x{addr:02X}")
                print(f"    CMD:    0x{resp_cmd:04X}")
                print(f"    LEN:    {data_len}")
                print(f"    STATUS: 0x{status:02X}")

                if len(response) > 6:
                    data = response[6:-2] if len(response) > 8 else b""
                    if data:
                        print(f"    DATA:   {data.hex().upper()}")
                        # Try ASCII decode
                        try:
                            ascii_view = data.rstrip(b"\x00").decode(
                                "ascii", errors="replace"
                            )
                            if ascii_view.isprintable():
                                print(f"    ASCII:  {ascii_view}")
                        except:
                            pass
                return True
            else:
                # Non-RFID response - maybe ASCII?
                try:
                    ascii_response = response.decode("ascii", errors="replace")
                    print(f"  ASCII: {ascii_response[:200]}")
                except:
                    pass
                return True
        else:
            print("  No response (empty)")
            return False

    except socket.timeout:
        print(f"  TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main(ip: str, port: int):
    print("=" * 70)
    print(f"M-200 Device Info Test")
    print(f"Target: {ip}:{port}")
    print("=" * 70)

    # Connect
    print(f"\nConnecting to {ip}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((ip, port))
        print(f"✓ Connected!")

        # Wait a moment for device to be ready
        import time

        time.sleep(0.2)

        # Clear any buffered data
        sock.setblocking(False)
        try:
            buffered = sock.recv(4096)
            if buffered:
                print(f"\nBuffered data on connect: {buffered.hex().upper()}")
        except:
            pass
        sock.setblocking(True)

        # Try each command
        for cmd, desc in COMMANDS.items():
            try_command(sock, cmd, desc)
            import time

            time.sleep(0.5)  # Small delay between commands

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("\n" + "=" * 70)
        print("Test complete")
        print("=" * 70)


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    main(ip, port)
