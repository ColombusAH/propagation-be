import socket
import struct
import time

# Configuration - Use 4001 if reader was configured for it
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4001  # Reader is configured for 4001

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

def parse_tag(payload):
    """Parse tag from inventory response"""
    if len(payload) < 9:
        return None
    # TagInfo structure from SDK:
    # WORD reserve, SHORT rssi, BYTE antenna, BYTE channel, BYTE reserve, BYTE reserve,
    # BYTE codeLen, BYTE code[255]
    rssi = struct.unpack(">h", payload[2:4])[0]
    antenna = payload[4]
    channel = payload[5]
    code_len = payload[8]
    if len(payload) < 9 + code_len:
        return None
    epc = payload[9:9+code_len]
    return {'rssi': rssi, 'antenna': antenna, 'channel': channel, 'epc': epc.hex().upper()}

def main():
    print("=" * 60)
    print("CORRECTED INVENTORY (Port 2022)")
    print("Based on UHFPrimeReader.DLL User Guide")
    print("=" * 60)
    print(f"\nListening on {LISTEN_IP}:{LISTEN_PORT}...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(1)
    
    print("Waiting for reader connection...")
    conn, addr = server.accept()
    print(f"[+] Connected: {addr[0]}:{addr[1]}")
    
    # 1. Get Device Info (0x0070)
    print("\n1. Getting Device Info...")
    conn.send(build_command(0x0070))
    conn.settimeout(3.0)
    
    try:
        response = conn.recv(4096)
        if response:
            print(f"   Response: {response.hex().upper()[:60]}...")
    except socket.timeout:
        print("   Timeout (will continue)")
    
    time.sleep(0.5)
    
    # 2. Start Continuous Inventory (0x0001)
    # From SDK: InventoryContinue(invCount=0x00, invParam=0)
    # invCount: 0x00 = by time, 0x03 = custom
    # invParam: 4 bytes, if 0 = continue until stop
    print("\n2. Starting Continuous Inventory (0x0001)...")
    inv_payload = struct.pack("B", 0x00)  # invCount = by time
    inv_payload += struct.pack(">I", 0)   # invParam = 0 (continuous)
    conn.send(build_command(0x0001, inv_payload))
    
    print("\n📡 Listening for Tags (60 seconds)...")
    print("   Move tags through the gate now!")
    print("-" * 60)
    
    conn.settimeout(1.0)
    buffer = b""
    tags = {}
    frame_count = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < 60:
            try:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                
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
                    
                    frame_count += 1
                    
                    # STAT_OK = 0x00 means tag found
                    if status == 0x00 and len(payload) >= 9:
                        tag = parse_tag(payload)
                        if tag and tag['epc']:
                            epc = tag['epc']
                            if epc not in tags:
                                tags[epc] = 0
                                print(f"🆕 NEW TAG #{len(tags)}: {epc}")
                                print(f"   RSSI: {tag['rssi']}, Ant: {tag['antenna']}, Ch: {tag['channel']}")
                            tags[epc] += 1
                    elif cmd == 0x0082:
                        # Gate status report - try to extract tag from it
                        if len(payload) > 10:
                            # CUSTOMERINFO might contain EPC
                            for i in range(len(payload) - 12):
                                if payload[i:i+2] == b'\xE2\x80':  # Common EPC prefix
                                    epc = payload[i:i+12].hex().upper()
                                    if epc not in tags:
                                        tags[epc] = 0
                                        print(f"🆕 GATE TAG #{len(tags)}: {epc}")
                                    tags[epc] += 1
                                    break
                        
            except socket.timeout:
                continue
                
    except KeyboardInterrupt:
        print("\nStopped by user.")
    
    # 3. Stop Inventory
    print("\n3. Stopping Inventory...")
    conn.send(build_command(0x0050))
    
    print("-" * 60)
    print(f"\n=== SUMMARY ===")
    print(f"Total Frames: {frame_count}")
    print(f"Unique Tags: {len(tags)}")
    for i, (epc, count) in enumerate(sorted(tags.items(), key=lambda x: -x[1]), 1):
        print(f"  {i}. {epc} (seen {count}x)")
    
    conn.close()
    server.close()

if __name__ == "__main__":
    main()
