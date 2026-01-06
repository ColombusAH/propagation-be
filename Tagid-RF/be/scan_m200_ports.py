#!/usr/bin/env python3
"""
Scan M-200 for open ports and test which ones respond to RFID commands.
"""

import socket
import struct
import sys

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


def build_command() -> bytes:
    """Build RFM_GET_DEVICE_INFO command"""
    frame = struct.pack('>BBHB', HEAD, BROADCAST_ADDR, CMD_GET_DEVICE_INFO, 0)
    crc = calculate_crc16(frame)
    frame += struct.pack('<H', crc)
    return frame


def test_port(ip: str, port: int, timeout: float = 2.0) -> dict:
    """Test if port is open and responds to RFID commands"""
    result = {
        "port": port,
        "open": False,
        "responds_to_rfid": False,
        "response": None,
        "error": None
    }
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        # Try to connect
        sock.connect((ip, port))
        result["open"] = True
        
        # Send RFID command
        cmd = build_command()
        sock.sendall(cmd)
        
        # Try to receive response
        try:
            header = sock.recv(6, socket.MSG_DONTWAIT)
            if header and len(header) > 0:
                result["responds_to_rfid"] = True
                result["response"] = header.hex().upper()
        except:
            pass
            
    except socket.timeout:
        result["error"] = "Connection timeout"
    except ConnectionRefusedError:
        result["error"] = "Connection refused"
    except Exception as e:
        result["error"] = str(e)
    finally:
        sock.close()
    
    return result


def scan_ports(ip: str):
    """Scan common RFID reader ports"""
    print("=" * 70)
    print(f"Scanning M-200 at {ip}")
    print("=" * 70)
    
    # Common RFID reader ports
    ports_to_scan = [
        (4001, "Standard Chafon port"),
        (5000, "Alternative port 1"),
        (6000, "Alternative port 2"),
        (2022, "HTTP/Config port"),
        (27011, "CF-RU reader port"),
        (10001, "Alternative port 3"),
        (9090, "Alternative port 4"),
    ]
    
    results = []
    
    for port, description in ports_to_scan:
        print(f"\nTesting port {port} ({description})...")
        result = test_port(ip, port)
        results.append(result)
        
        if result["open"]:
            print(f"  ✓ Port {port} is OPEN")
            if result["responds_to_rfid"]:
                print(f"  ✓ Responds to RFID commands!")
                print(f"    Response: {result['response']}")
            else:
                print(f"  ⚠️  Port open but no RFID response")
        else:
            print(f"  ✗ Port {port} is CLOSED ({result['error']})")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    open_ports = [r for r in results if r["open"]]
    rfid_ports = [r for r in results if r["responds_to_rfid"]]
    
    if rfid_ports:
        print(f"\n✓ Found {len(rfid_ports)} port(s) responding to RFID commands:")
        for r in rfid_ports:
            print(f"  - Port {r['port']}")
        print(f"\nUpdate your .env file:")
        print(f"  RFID_READER_PORT={rfid_ports[0]['port']}")
    elif open_ports:
        print(f"\n⚠️  Found {len(open_ports)} open port(s), but none respond to RFID commands:")
        for r in open_ports:
            print(f"  - Port {r['port']}")
        print(f"\nPossible issues:")
        print(f"  1. M-200 might use HTTP/REST API instead of raw TCP")
        print(f"  2. Different protocol version")
        print(f"  3. M-200 in configuration mode")
    else:
        print("\n✗ No open ports found")
        print("\nPossible issues:")
        print("  1. M-200 TCP server not enabled")
        print("  2. Firewall blocking ports")
        print("  3. Wrong IP address")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan M-200 for RFID ports")
    parser.add_argument("--ip", default="169.254.128.161", help="M-200 IP address")
    
    args = parser.parse_args()
    scan_ports(args.ip)


