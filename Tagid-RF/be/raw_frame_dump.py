import socket
import time

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4001

def main():
    print("=== RAW FRAME DUMP (No Parsing) ===")
    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)
    
    conn, addr = server.accept()
    print(f"\n[+] Connected: {addr[0]}")
    print("Dumping raw frames for 30 seconds...\n")
    print("-" * 80)
    
    conn.settimeout(30.0)
    buffer = b""
    frame_count = 0
    unique_epcs = set()
    
    try:
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                chunk = conn.recv(4096)
                if not chunk: break
                buffer += chunk
                
                # Parse frames
                while len(buffer) >= 7:
                    if buffer[0] != 0xCF:
                        idx = buffer.find(b'\xCF', 1)
                        if idx != -1: 
                            buffer = buffer[idx:]
                        else: 
                            buffer = b""
                        continue

                    length = buffer[4]
                    if len(buffer) < 7 + length: 
                        break
                    
                    frame = buffer[:7+length]
                    buffer = buffer[7+length:]
                    
                    cmd = (frame[2] << 8) | frame[3]
                    status = frame[5]
                    payload = frame[6:-2]
                    
                    # Only show tag data frames (0x0082 or 0x0001)
                    if cmd == 0x0082 or cmd == 0x0001:
                        frame_count += 1
                        full_hex = frame.hex().upper()
                        payload_hex = payload.hex().upper() if payload else "EMPTY"
                        
                        # Try to extract EPC (bytes 2 onwards in payload, skip Ant+RSSI)
                        if len(payload) > 2:
                            # Skip first 2 bytes (Ant, RSSI)
                            epc_part = payload[2:]
                            # Strip trailing zeros
                            while epc_part and epc_part[-1] == 0:
                                epc_part = epc_part[:-1]
                            epc_hex = epc_part.hex().upper() if epc_part else "EMPTY"
                        else:
                            epc_hex = "TOO_SHORT"
                        
                        is_new = epc_hex not in unique_epcs and epc_hex not in ["EMPTY", "TOO_SHORT"]
                        if is_new:
                            unique_epcs.add(epc_hex)
                        
                        marker = "🆕" if is_new else "  "
                        print(f"{marker} Frame #{frame_count:03d} | CMD: 0x{cmd:04X} | Len: {length:02d} | EPC Parsed: {epc_hex}")
                        print(f"   Full: {full_hex}")
                        print()
                        
            except socket.timeout:
                break
                
    except KeyboardInterrupt:
        print("\nStopped.")
    
    print("-" * 80)
    print(f"\n=== SUMMARY ===")
    print(f"Total Frames: {frame_count}")
    print(f"Unique EPCs: {len(unique_epcs)}")
    for i, epc in enumerate(sorted(unique_epcs), 1):
        print(f"  {i}. {epc}")
    
    conn.close()
    server.close()

if __name__ == "__main__":
    main()
