import socket
import time

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4001

def parse_tag_response(payload):
    """
    Parse tag response according to manual Section 2.3.1
    Response payload format:
    - RSSI: 2 bytes
    - Antenna: 1 byte
    - Channel: 1 byte
    - EPC LEN: 1 byte
    - EPC NUM: N bytes (length specified by EPC LEN)
    """
    if len(payload) < 5:
        return None
    
    rssi = (payload[0] << 8) | payload[1]
    antenna = payload[2]
    channel = payload[3]
    epc_len = payload[4]
    
    if len(payload) < 5 + epc_len:
        return None
    
    epc = payload[5:5+epc_len]
    
    return {
        'rssi': rssi,
        'antenna': antenna,
        'channel': channel,
        'epc_len': epc_len,
        'epc': epc.hex().upper()
    }

def main():
    print("=== PASSIVE LISTENER (Active Mode) ===")
    print("This script does NOT send any commands.")
    print("It only listens for automatic tag reports (0x0082).")
    print(f"\nListening on {LISTEN_IP}:{LISTEN_PORT}...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)
    
    conn, addr = server.accept()
    print(f"\n[+] Connected: {addr[0]}")
    print("\n📡 Passively listening for 60 seconds...")
    print("   (Tags should appear automatically in Active Mode)")
    print("-" * 60)
    
    conn.settimeout(60.0)
    buffer = b""
    tags = {}  # EPC -> count
    frame_count = 0
    
    try:
        start_time = time.time()
        while time.time() - start_time < 60:
            try:
                chunk = conn.recv(4096)
                if not chunk: break
                buffer += chunk
                
                while len(buffer) >= 7:
                    if buffer[0] != 0xCF:
                        idx = buffer.find(b'\xCF', 1)
                        if idx != -1: buffer = buffer[idx:]
                        else: buffer = b""
                        continue

                    length = buffer[4]
                    if len(buffer) < 7 + length: 
                        break
                    
                    frame = buffer[:7+length]
                    buffer = buffer[7+length:]
                    
                    cmd = (frame[2] << 8) | frame[3]
                    status = frame[5]
                    payload = frame[6:-2]
                    
                    # Only process tag frames (0x0082 = Active Mode report)
                    if cmd == 0x0082:
                        frame_count += 1
                        
                        # Try to parse as tag data
                        tag = parse_tag_response(payload)
                        if tag and tag['epc'] and tag['epc_len'] > 0:
                            epc = tag['epc']
                            if epc not in tags:
                                tags[epc] = 0
                                print(f"🆕 NEW TAG #{len(tags)}: {epc}")
                                print(f"   RSSI: {tag['rssi']}, Ant: {tag['antenna']}, Len: {tag['epc_len']}")
                            tags[epc] += 1
                        else:
                            # Show raw frame for debugging
                            if frame_count <= 5:  # Only first 5
                                print(f"   [Frame #{frame_count}] Raw: {payload.hex().upper()[:40]}...")
                    else:
                        # Other command - log it
                        print(f"   [Other CMD: 0x{cmd:04X}, Status: 0x{status:02X}]")
                            
            except socket.timeout:
                break
                
    except KeyboardInterrupt:
        print("\nStopped by user.")
    
    print("-" * 60)
    print(f"\n=== SUMMARY ===")
    print(f"Total 0x0082 Frames: {frame_count}")
    print(f"Unique Tags: {len(tags)}")
    for i, (epc, count) in enumerate(sorted(tags.items(), key=lambda x: -x[1]), 1):
        print(f"  {i}. {epc} (seen {count}x)")
    
    conn.close()
    server.close()

if __name__ == "__main__":
    main()
