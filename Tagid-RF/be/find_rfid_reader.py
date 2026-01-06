#!/usr/bin/env python3
"""
Scan local network to find Chafon RFID readers.
Looks for devices responding to RFID protocol on common ports.
"""

import socket
import struct
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def test_rfid_device(ip: str, port: int, timeout: float = 1.0) -> dict:
    """Test if device at IP:port is an RFID reader"""
    result = {
        "ip": ip,
        "port": port,
        "is_rfid": False,
        "response": None,
        "error": None
    }
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        # Connect
        sock.connect((ip, port))
        
        # Send RFID command
        cmd = build_command()
        sock.sendall(cmd)
        
        # Try to receive response (header = 6 bytes)
        header = sock.recv(6)
        
        # Check if it looks like RFID response
        if len(header) >= 6 and header[0] == HEAD:
            result["is_rfid"] = True
            result["response"] = header.hex().upper()
            
            # Try to get device info
            data_len = header[4]
            status = header[5]
            
            if status == 0x00 and data_len > 0:
                # Read data + CRC
                remaining = sock.recv(data_len + 2)
                full_response = header + remaining
                
                if data_len >= 24:
                    data = remaining[:data_len]
                    result["device_info"] = {
                        "rfid_fw": f"{data[6]}.{data[7]}",
                        "serial": data[8:24].hex().upper()
                    }
    
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass
    except Exception as e:
        result["error"] = str(e)
    finally:
        sock.close()
    
    return result


def scan_network(base_ip: str):
    """Scan network for RFID readers"""
    print("=" * 70)
    print("Scanning Network for Chafon RFID Readers")
    print("=" * 70)
    print(f"\nBase IP: {base_ip}.x")
    print("Ports: 4001, 5000, 6000, 8080, 9090, 27011")
    print("\nThis may take a few minutes...\n")
    
    # Common RFID ports
    ports = [4001, 5000, 6000, 8080, 9090, 27011]
    
    # IP range to scan
    ip_range = range(1, 255)
    
    found_devices = []
    scanned = 0
    total = len(ip_range) * len(ports)
    
    # Scan in parallel
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        
        for i in ip_range:
            ip = f"{base_ip}.{i}"
            for port in ports:
                futures.append(executor.submit(test_rfid_device, ip, port, 0.5))
        
        for future in as_completed(futures):
            scanned += 1
            if scanned % 100 == 0:
                print(f"Progress: {scanned}/{total} ({scanned*100//total}%)", end='\r')
            
            result = future.result()
            if result["is_rfid"]:
                found_devices.append(result)
                print(f"\n✓ Found RFID reader at {result['ip']}:{result['port']}")
                if "device_info" in result:
                    print(f"  Firmware: {result['device_info']['rfid_fw']}")
                    print(f"  Serial: {result['device_info']['serial']}")
    
    print(f"\n\nScan complete: {scanned}/{total} checked")
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    if found_devices:
        print(f"\n✓ Found {len(found_devices)} RFID reader(s):\n")
        for device in found_devices:
            print(f"  IP: {device['ip']}")
            print(f"  Port: {device['port']}")
            if "device_info" in device:
                print(f"  Firmware: {device['device_info']['rfid_fw']}")
                print(f"  Serial: {device['device_info']['serial']}")
            print()
        
        print("Update your .env file:")
        print(f"  RFID_READER_IP={found_devices[0]['ip']}")
        print(f"  RFID_READER_PORT={found_devices[0]['port']}")
    else:
        print("\n✗ No RFID readers found")
        print("\nPossible reasons:")
        print("  1. RFID reader not on this network")
        print("  2. RFID reader TCP server not enabled")
        print("  3. Different network subnet")
        print("  4. Firewall blocking connections")
        print("\nTry:")
        print("  1. Check RFID reader's actual IP (on device display/settings)")
        print("  2. Make sure reader and computer are on same network")
        print("  3. Enable TCP server in reader settings")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Find Chafon RFID readers on network")
    parser.add_argument(
        "--subnet",
        default="169.254.173",
        help="Network subnet to scan (e.g., 192.168.1 or 169.254.173)"
    )
    
    args = parser.parse_args()
    
    # Extract base IP (first 3 octets)
    parts = args.subnet.split('.')
    if len(parts) != 3:
        print("Error: Subnet must be 3 octets (e.g., 192.168.1)")
        sys.exit(1)
    
    base_ip = args.subnet
    
    try:
        scan_network(base_ip)
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan interrupted by user")


