import socket
import struct
import time

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
    print("=== PROPER INVENTORY (Manual Section 2.3.1) ===")
    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)
    
    conn, addr = server.accept()
    print(f"\n[+] Connected: {addr[0]}")
    
    # 1. Stop first
    print("\n1. Sending STOP (0x0050)...")
    conn.send(build_command(0x0050))
    
    time.sleep(1.0)
    
    # 2. Start Inventory with proper format
    # InvType = 0x00 (count by time)
    # InvParam = 0x00000000 (continue until stop command)
    print("\n2. Starting Inventory (0x0001)...")
    print("   InvType=0x00 (by time), InvParam=0 (continuous)")
    inv_payload = b'\x00\x00\x00\x00\x00'  # 5 bytes: InvType(1) + InvParam(4)
    conn.send(build_command(0x0001, inv_payload))
    
    print("\n📡 Listening for Tags (30 seconds)...")
    print("-" * 60)
    
    conn.settimeout(30.0)
    buffer = b""
    tags = {}  # EPC -> count
    frame_count = 0
    
    try:
        start_time = time.time()
        while time.time() - start_time < 30:
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
                    
                    # Tag data frames
                    if cmd == 0x0001 or cmd == 0x0082:
                        frame_count += 1
                        
                        # Status 0x00 = tag found
                        if status == 0x00:
                            tag = parse_tag_response(payload)
                            if tag and tag['epc']:
                                epc = tag['epc']
                                if epc not in tags:
                                    tags[epc] = 0
                                    print(f"🆕 NEW TAG #{len(tags)}: {epc}")
                                    print(f"   RSSI: {tag['rssi']}, Ant: {tag['antenna']}, Ch: {tag['channel']}, Len: {tag['epc_len']}")
                                tags[epc] += 1
                        elif status == 0x12:
                            print(f"   [i] Inventory cycle complete (Status 0x12)")
                        else:
                            print(f"   [?] Frame with status: 0x{status:02X}")
                            print(f"       Payload: {payload.hex().upper()}")
                            
            except socket.timeout:
                break
                
    except KeyboardInterrupt:
        print("\nStopped.")
    
    print("-" * 60)
    print(f"\n=== SUMMARY ===")
    print(f"Total Frames: {frame_count}")
    print(f"Unique Tags: {len(tags)}")
    for i, (epc, count) in enumerate(sorted(tags.items()), 1):
        print(f"  {i}. {epc} (seen {count}x)")
    
    conn.close()
    server.close()

if __name__ == "__main__":
    main()
