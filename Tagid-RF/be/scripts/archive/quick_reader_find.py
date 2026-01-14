#!/usr/bin/env python3
"""
Quick script to find RFID reader on direct connection.
Tests common IPs and ports quickly.
"""

import socket
import struct

HEAD = 0xCF
BROADCAST_ADDR = 0xFF
CMD_GET_DEVICE_INFO = 0x0021
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


def build_command() -> bytes:
    frame = struct.pack('>BBHB', HEAD, BROADCAST_ADDR, CMD_GET_DEVICE_INFO, 0)
    crc = calculate_crc16(frame)
    frame += struct.pack('<H', crc)
    return frame


def test_ip_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    """Quick test if device responds to RFID command"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.sendall(build_command())
        response = sock.recv(6)
        sock.close()
        return len(response) >= 6 and response[0] == HEAD
    except:
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Quick RFID Reader Discovery")
    print("=" * 60)
    print("\nTesting common IPs and ports...\n")
    
    # Common IPs to test
    ips_to_test = [
        "192.168.1.200",
        "192.168.1.1",
        "192.168.1.2",
        "192.168.1.10",
        "192.168.1.50",
        "169.254.203.1",
        "169.254.203.100",
        "169.254.1.1",
        "169.254.1.100",
    ]
    
    # Common ports
    ports_to_test = [4001, 5000, 6000, 8080, 9090]
    
    found = False
    
    for ip in ips_to_test:
        for port in ports_to_test:
            print(f"Testing {ip}:{port}...", end=" ")
            if test_ip_port(ip, port, 0.5):
                print(f"✓ FOUND RFID READER!")
                print(f"\n{'='*60}")
                print(f"Reader IP: {ip}")
                print(f"Reader Port: {port}")
                print(f"{'='*60}")
                print(f"\nUpdate your .env:")
                print(f"  RFID_READER_IP={ip}")
                print(f"  RFID_READER_PORT={port}")
                found = True
                break
            else:
                print("✗")
        if found:
            break
    
    if not found:
        print("\n" + "=" * 60)
        print("No RFID reader found")
        print("=" * 60)
        print("\nPossible reasons:")
        print("  1. Reader TCP server not enabled")
        print("  2. Reader not configured with static IP")
        print("  3. Reader still using link-local IP (169.254.x.x)")
        print("  4. Reader needs to be configured via:")
        print("     - Device display menu")
        print("     - Web interface")
        print("     - Configuration software")
        print("\nNext steps:")
        print("  1. Check reader display for IP address")
        print("  2. Try accessing web interface:")
        print("     - http://192.168.1.200")
        print("     - http://169.254.203.1")
        print("  3. Enable TCP server in reader settings")


