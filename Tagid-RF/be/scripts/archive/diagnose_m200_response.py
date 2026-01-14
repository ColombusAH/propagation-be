#!/usr/bin/env python3
"""
Diagnostic script to inspect raw M-200 responses
"""
import socket
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.services.m200_protocol import (
    build_get_device_info_command,
    M200Command,
    M200Commands,
    HEAD
)

def hex_dump(data: bytes, prefix="") -> str:
    """Create hex dump of bytes"""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"{prefix}{i:04X}: {hex_str:<48} {ascii_str}")
    return '\n'.join(lines)

def test_connection(ip: str, port: int, timeout: int = 10):
    """Test connection and inspect raw response"""
    print(f"Connecting to {ip}:{port} (timeout: {timeout}s)...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        print("✓ Connected\n")
        
        # Send GET_DEVICE_INFO command
        cmd = build_get_device_info_command()
        cmd_bytes = cmd.serialize()
        
        print("=" * 70)
        print("SENDING COMMAND:")
        print("=" * 70)
        print(f"Command: {cmd}")
        print(f"Raw bytes ({len(cmd_bytes)} bytes):")
        print(hex_dump(cmd_bytes))
        print()
        
        # Send command
        sock.sendall(cmd_bytes)
        print("✓ Command sent, waiting for response...\n")
        
        # Try to read response with multiple strategies
        print("=" * 70)
        print("RECEIVING RESPONSE:")
        print("=" * 70)
        
        # Strategy 1: Read first 2 bytes (what we got)
        response_2 = sock.recv(2)
        print(f"First 2 bytes: {response_2.hex().upper()}")
        print(f"  As ASCII: {repr(response_2.decode('ascii', errors='replace'))}")
        print()
        
        # Strategy 2: Try to read more (with timeout)
        try:
            sock.settimeout(1)  # Short timeout for additional data
            response_more = sock.recv(1024)
            if response_more:
                print(f"Additional {len(response_more)} bytes received:")
                print(hex_dump(response_more))
                response_2 += response_more
        except socket.timeout:
            print("No additional data (timeout after 1s)")
        
        print()
        print("=" * 70)
        print("FULL RESPONSE ANALYSIS:")
        print("=" * 70)
        print(f"Total length: {len(response_2)} bytes")
        print(hex_dump(response_2))
        print()
        
        # Analyze first byte
        first_byte = response_2[0] if response_2 else None
        if first_byte:
            print(f"First byte: 0x{first_byte:02X} ({first_byte} decimal)")
            if first_byte == 0x43:
                print("  → This is ASCII 'C'")
                print("  → Possible text-based protocol or HTTP response")
            elif first_byte == HEAD:
                print(f"  → This matches expected HEAD (0x{HEAD:02X})")
            else:
                print(f"  → Expected HEAD: 0x{HEAD:02X}")
        
        # Check if it looks like HTTP
        if response_2.startswith(b'HTTP') or response_2.startswith(b'C'):
            print("\n⚠️  Response appears to be text-based (HTTP or text protocol)")
            print("   The M-200 might be using HTTP/REST API instead of binary protocol")
        
        sock.close()
        print("\n✓ Connection closed")
        
    except socket.timeout:
        print("✗ Connection timeout")
        sys.exit(1)
    except ConnectionRefusedError:
        print("✗ Connection refused")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Diagnose M-200 response format")
    parser.add_argument("--ip", type=str, default=os.getenv("RFID_READER_IP", "169.254.40.109"),
                       help="M-200 IP address")
    parser.add_argument("--port", type=int, default=int(os.getenv("RFID_READER_PORT", "2022")),
                       help="M-200 port")
    parser.add_argument("--timeout", type=int, default=10,
                       help="Socket timeout in seconds")
    
    args = parser.parse_args()
    test_connection(args.ip, args.port, args.timeout)







