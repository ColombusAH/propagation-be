#!/usr/bin/env python3
"""
Hybrid mode - read first, then send commands.
Based on observation that device may be in auto-inventory mode.
"""

import socket
import struct
import sys
import time
from datetime import datetime

HEAD = 0xCF
BROADCAST_ADDR = 0xFF
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


def extract_tags(data: bytes) -> list:
    """Extract any tags from a data buffer"""
    tags = []
    
    # Look for RFID frames
    i = 0
    while i < len(data):
        if data[i] == HEAD and i + 6 <= len(data):
            addr = data[i + 1]
            cmd = (data[i + 2] << 8) | data[i + 3]
            length = data[i + 4]
            status = data[i + 5]
            
            frame_end = i + 5 + length + 2
            if frame_end <= len(data) and cmd == 0x0001 and status == 0x00:
                # Inventory response with tags
                payload = data[i + 6:i + 5 + length]
                
                offset = 0
                while offset + 5 <= len(payload):
                    rssi = payload[offset]
                    ant = payload[offset + 1]
                    epc_len = payload[offset + 4]
                    
                    if offset + 5 + epc_len <= len(payload):
                        epc = payload[offset + 5:offset + 5 + epc_len]
                        tags.append({
                            'epc': epc.hex().upper(),
                            'rssi': -rssi,
                            'antenna': ant
                        })
                    offset += 5 + epc_len
                
                i = frame_end
                continue
        i += 1
    
    return tags


def hybrid_reader(ip: str, port: int, duration: int = 30):
    print("=" * 70)
    print(f"HYBRID RFID READER")
    print(f"Target: {ip}:{port}")
    print(f"Duration: {duration}s")
    print("=" * 70)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        print(f"\nConnecting...")
        sock.connect((ip, port))
        print("✓ Connected!")
        
        # Set non-blocking for mixed read/write
        sock.setblocking(False)
        
        start_time = time.time()
        seen_tags = set()
        total_reads = 0
        last_cmd_time = 0
        cmd_interval = 2.0  # Send command every 2 seconds
        
        print("\n🏷️  Bring tags close to the reader!")
        print("-" * 70)
        print(f"{'Time':<12} {'EPC':<28} {'RSSI':<8} {'Ant'}")
        print("-" * 70)
        
        # Build a simple get_device_info command to trigger response
        frame = struct.pack('>BBHB', HEAD, BROADCAST_ADDR, 0x0070, 0)
        crc = calculate_crc16(frame)
        trigger_cmd = frame + struct.pack('<H', crc)
        
        while time.time() - start_time < duration:
            # Periodically send a command to trigger device
            if time.time() - last_cmd_time > cmd_interval:
                try:
                    sock.sendall(trigger_cmd)
                    last_cmd_time = time.time()
                except:
                    pass
            
            # Try to read any available data
            try:
                data = sock.recv(4096)
                if data:
                    tags = extract_tags(data)
                    
                    for tag in tags:
                        total_reads += 1
                        epc = tag['epc']
                        is_new = epc not in seen_tags
                        seen_tags.add(epc)
                        
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        marker = "🆕" if is_new else "  "
                        print(f"{marker}{timestamp}  {epc:<28} {tag['rssi']:>4} dBm  {tag['antenna']}")
                    
                    # Also print raw if no tags but we got data
                    if not tags and len(data) > 6:
                        # Check if it's a device info response
                        if data[0] == HEAD:
                            cmd = (data[2] << 8) | data[3]
                            if cmd == 0x0070:
                                print(f"[Device info response received]")
                            elif cmd != 0x0001:
                                print(f"[CMD 0x{cmd:04X} response]")
                    
            except BlockingIOError:
                pass  # No data available
            except Exception as e:
                if "10035" not in str(e):  # Ignore WOULDBLOCK on Windows
                    print(f"Error: {e}")
            
            time.sleep(0.1)
        
        print("-" * 70)
        print(f"\n📊 Summary:")
        print(f"   Total reads: {total_reads}")
        print(f"   Unique tags: {len(seen_tags)}")
        if seen_tags:
            print(f"\n   Unique EPCs:")
            for epc in sorted(seen_tags):
                print(f"   - {epc}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()
        print("\nSocket closed")


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    hybrid_reader(ip, port, duration)
