#!/usr/bin/env python3
"""
Simple blocking reader - just read everything that comes.
"""

import socket
import sys

def simple_read(ip: str, port: int):
    print(f"Connecting to {ip}:{port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((ip, port))
    print("Connected!")
    
    # Read for 30 seconds
    import time
    start = time.time()
    total_bytes = 0
    
    print("\nListening (30s)... Bring tags near the reader!")
    print("-" * 60)
    
    while time.time() - start < 30:
        try:
            sock.settimeout(1)
            data = sock.recv(4096)
            if data:
                total_bytes += len(data)
                ts = time.strftime("%H:%M:%S")
                print(f"[{ts}] {len(data)} bytes: {data.hex().upper()}")
                
                # Quick parse
                if len(data) >= 6 and data[0] == 0xCF:
                    cmd = (data[2] << 8) | data[3]
                    length = data[4]
                    status = data[5]
                    print(f"        CMD=0x{cmd:04X} LEN={length} STATUS=0x{status:02X}")
                    
                    if cmd == 0x0001 and status == 0x00 and length > 5:
                        # Tag data!
                        payload = data[6:6+length-1]
                        if len(payload) >= 5:
                            epc_len = payload[4]
                            if len(payload) >= 5 + epc_len:
                                epc = payload[5:5+epc_len].hex().upper()
                                rssi = -payload[0]
                                print(f"        📍 TAG: {epc}, RSSI: {rssi}dBm")
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error: {e}")
            break
    
    sock.close()
    print("-" * 60)
    print(f"Total: {total_bytes} bytes received")


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    simple_read(ip, port)
