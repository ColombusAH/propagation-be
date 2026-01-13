"""
Debug Script: Test Multi-Tag Detection (Server Mode) v2
Fixed parsing to extract EPC from END of data (after zero padding).
"""

import socket
import time

# Configuration
LISTEN_PORT = 4001
TIMEOUT = 60

# M-200 Protocol constants
HEAD = 0xCF

def extract_epc_from_payload(payload: bytes):
    """Extract EPC from the END of payload (after zero padding)."""
    if not payload:
        return None
    
    # Find non-zero bytes from the end
    end_idx = len(payload)
    start_idx = end_idx
    
    for i in range(len(payload) - 1, -1, -1):
        if payload[i] != 0:
            end_idx = i + 1
            start_idx = i
            # Walk back to find start of EPC
            while start_idx > 0 and payload[start_idx - 1] != 0:
                start_idx -= 1
            break
    
    if start_idx < end_idx:
        return payload[start_idx:end_idx].hex().upper()
    return None

def main():
    print("=" * 60)
    print("M-200 Multi-Tag Detection Debug v2")
    print("=" * 60)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", LISTEN_PORT))
    server.listen(1)
    server.settimeout(TIMEOUT)
    
    print(f"🎧 Listening on port {LISTEN_PORT}...")
    print("   Waiting for M-200 reader to connect...")
    print("-" * 60)
    
    all_tags = set()
    
    try:
        conn, addr = server.accept()
        print(f"\n✅ Reader connected from {addr[0]}:{addr[1]}")
        conn.settimeout(2)
        
        buffer = b""
        start_time = time.time()
        
        print("\n📡 Listening for tags... (Press Ctrl+C to stop)")
        print("   Place tags near the reader antenna!")
        print("-" * 60)
        
        while time.time() - start_time < 60:
            try:
                chunk = conn.recv(1024)
                if not chunk:
                    print("Connection closed by reader")
                    break
                
                buffer += chunk
                
                # Process frames
                while len(buffer) >= 7:
                    if buffer[0] != HEAD:
                        idx = buffer.find(bytes([HEAD]), 1)
                        if idx > 0:
                            buffer = buffer[idx:]
                        else:
                            buffer = b""
                        continue
                    
                    if len(buffer) < 5:
                        break
                    
                    length = buffer[4]
                    frame_len = 7 + length  # HD + ADDR + CMD(2) + LEN + DATA + CRC(2)
                    
                    if len(buffer) < frame_len:
                        break
                    
                    frame = buffer[:frame_len]
                    buffer = buffer[frame_len:]
                    
                    cmd = (frame[2] << 8) | frame[3]
                    
                    # Only process tag notifications (0x0082)
                    if cmd == 0x0082 and length > 5:
                        data = frame[5:-2]  # Skip header, cmd, len and CRC
                        # 0x0082 format observed: [Ant][RSSI][...EPC...]
                        if len(data) > 2:
                            payload = data[2:] # Skip Ant(1) and RSSI(1)
                        else:
                            payload = data
                        
                        epc = extract_epc_from_payload(payload)
                        
                        if epc and epc not in all_tags and len(epc) >= 4:
                            all_tags.add(epc)
                            print(f"\n🏷️  *** NEW TAG #{len(all_tags)} ***")
                            print(f"    EPC: {epc}")
                            print(f"    Length: {len(epc)//2} bytes")
                
            except socket.timeout:
                continue
                
    except socket.timeout:
        print("❌ Timeout - no reader connected")
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        server.close()
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: Found {len(all_tags)} unique tags")
    print("=" * 60)
    for i, epc in enumerate(sorted(all_tags), 1):
        print(f"  {i}. {epc}")
    print("=" * 60)

if __name__ == "__main__":
    main()
