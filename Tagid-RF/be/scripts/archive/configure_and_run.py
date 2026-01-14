import socket
import struct
import time
import sys

# Configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4001

def calculate_crc16(data: bytes) -> int:
    PRESET_VALUE = 0xFFFF
    POLYNOMIAL = 0x8408
    crc_value = PRESET_VALUE
    for byte in data:
        crc_value ^= byte
        for _ in range(8):
            if crc_value & 0x0001:
                crc_value = (crc_value >> 1) ^ POLYNOMIAL
            else:
                crc_value = crc_value >> 1
    return crc_value

def build_command(cmd_code: int, data: bytes = b"", addr: int = 0xFF) -> bytes:
    head = 0xCF
    frame_body = struct.pack(">BBBB", head, addr, (cmd_code >> 8) & 0xFF, cmd_code & 0xFF)
    frame_body += struct.pack("B", len(data))
    frame_body += data
    crc = calculate_crc16(frame_body)
    return frame_body + struct.pack(">H", crc)

def drain_socket(client, duration=0.5):
    end_time = time.time() + duration
    client.settimeout(0.1)
    try:
        while time.time() < end_time:
            chunk = client.recv(4096)
            if not chunk: break
    except socket.timeout:
        pass
    client.settimeout(None) # Blocking for main loop (or specific timeout later)

def wait_for_response(client, expected_cmd, timeout=3.0):
    client.settimeout(timeout)
    start_time = time.time()
    buffer = b""
    try:
        while time.time() - start_time < timeout:
            chunk = client.recv(4096)
            if not chunk: break
            buffer += chunk
            
            while len(buffer) >= 6:
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
                
                if cmd == expected_cmd:
                    return True, status
                elif cmd == 0x0082:
                    continue
                    
    except socket.timeout:
        return False, "Timeout"
    return False, "Not Found"

def extract_epc(payload):
    # Skip Ant(1) and RSSI(1) -> Start at index 2
    if len(payload) < 3: return None
    core_payload = payload[2:]
    
    # Strip trailing zeros provided as padding
    # E.g., [E2 80 ... 00 00]
    # We want the data up to the last non-zero byte
    real_len = len(core_payload)
    while real_len > 0 and core_payload[real_len-1] == 0:
        real_len -= 1
        
    if real_len == 0: return None
    return core_payload[:real_len].hex().upper()

def main():
    print("=== RFID CONFIGURE & RUN (Gate Reader) ===")
    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)
    
    conn, addr = server.accept()
    print(f"\n[+] Connected: {addr[0]}")
    
    # 1. Stop
    print("1. Sending STOP (0x0050)...")
    drain_socket(conn)
    conn.send(build_command(0x0050))
    success, status = wait_for_response(conn, 0x0050)
    if success and status == 0x00:
        print("   ✅ Stopped.")
    else:
        print(f"   ⚠️ Stop failed/No ACK ({status}). Treating as Stopped.")

    time.sleep(1.0)

    time.sleep(1.0)

    # 2. Configure Session 1 (Target=0, Q=4) - BEST for Multi-Tag
    print("2. Setting Query: Session 1, Q=4 (0x0012 payload=[04, 01, 00])...")
    # Payload: [Q=4, Session=1, Target=0]
    conn.send(build_command(0x0012, b'\x04\x01\x00'))
    success, status = wait_for_response(conn, 0x0012)
    if success and status == 0x00:
        print("   ✅ Configured Session 1 (Multi-Tag Mode).")
    else:
        print(f"   ⚠️ Session 1 Config Failed (Status {status}). Trying Session 0...")
        
        # Fallback to Session 0
        conn.send(build_command(0x0012, b'\x04\x00\x00'))
        success, status = wait_for_response(conn, 0x0012)
        if success and status == 0x00:
             print("   ✅ Configured Session 0.")
        else:
             print("   ❌ All Configs Failed. Continuing with default settings...")

    time.sleep(0.5)

    # 3. Start Inventory
    print("3. Starting Inventory (0x0001)...")
    # Check if necessary? Gate readers sometimes resume automatically or need specific start
    # We will try sending 0x0001
    conn.send(build_command(0x0001, b'\x00\x00'))
    
    print("\n📡 Listening for Tags (Ctrl+C to stop)...")
    print("-" * 50)
    
    conn.settimeout(None)
    buffer = b""
    tags = set()
    
    try:
        while True:
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
                 if len(buffer) < 7 + length: break
                 
                 frame = buffer[:7+length]
                 buffer = buffer[7+length:]
                 
                 cmd = (frame[2] << 8) | frame[3]
                 
                 if cmd == 0x0082 or cmd == 0x0001: # Tag Data
                     data = frame[5:-2]
                     # Check if it has payload
                     if len(data) > 2:
                         epc = extract_epc(data)
                         if epc and epc not in tags:
                             tags.add(epc)
                             print(f"🏷️  NEW TAG #{len(tags)}: {epc}")
                             
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    main()
