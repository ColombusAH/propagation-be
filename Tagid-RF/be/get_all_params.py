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
                data = frame[6:-2]
                
                if cmd == expected_cmd:
                    return True, status, data
                elif cmd == 0x0082:
                    continue
                    
    except socket.timeout:
        return False, "Timeout", None
    return False, "Not Found", None

def parse_all_params(data):
    """Parse the response from RFM_GET_ALL_PARAM (0x0072)"""
    if len(data) < 26:
        print(f"   Data too short: {len(data)} bytes (expected 26+)")
        return None
    
    # Based on manual Section 2.2.9
    # Payload structure (after status byte):
    # Addr(1) + RFIDPRO(1) + WorkMode(1) + Interface(1) + Baudrate(1) + WGSet(1) + Ant(1) + RfidFreq(8)
    # + RfidPower(1) + InquiryArea(1) + QValue(1) + Session(1) + AcsAddr(1) + AcsDataLen(1) 
    # + FilterTime(1) + TriggerTime(1) + BuzzerTime(1) + PollingInterval(1)
    
    params = {
        'Addr': data[0],
        'RFIDPRO': data[1],
        'WorkMode': data[2],
        'Interface': data[3],
        'Baudrate': data[4],
        'WGSet': data[5],
        'Ant': data[6],
        'RfidFreq': data[7:15].hex().upper(),
        'RfidPower': data[15],
        'InquiryArea': data[16],
        'QValue': data[17],
        'Session': data[18],
        'AcsAddr': data[19],
        'AcsDataLen': data[20],
        'FilterTime': data[21],
        'TriggerTime': data[22],
        'BuzzerTime': data[23],
        'PollingInterval': data[24],
    }
    
    return params

def main():
    print("=== GET ALL PARAMS (0x0072) ===")
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
    success, status, _ = wait_for_response(conn, 0x0050)
    if success: print("   ✅ Stopped.")
    else: print("   ⚠️ Stop Failed.")
    
    time.sleep(1.0)
    
    # 2. Get All Params (0x0072)
    print("\n2. Getting All Params (0x0072)...")
    conn.send(build_command(0x0072))
    success, status, data = wait_for_response(conn, 0x0072)
    
    if success and data:
        print(f"   ✅ SUCCESS! Status: {status}")
        print(f"   📦 Raw Data ({len(data)} bytes): {data.hex().upper()}")
        
        params = parse_all_params(data)
        if params:
            print("\n" + "=" * 50)
            print("PARSED PARAMETERS:")
            print("=" * 50)
            
            # Work Mode
            work_modes = {0: "Answer Mode", 1: "Active Mode", 2: "Trigger Mode"}
            print(f"  WorkMode:    {params['WorkMode']} ({work_modes.get(params['WorkMode'], 'Unknown')})")
            
            # Critical params
            print(f"  QValue:      {params['QValue']} ⭐ (0-15, higher = more tags)")
            print(f"  Session:     {params['Session']} ⭐ (0=continuous, 1-3=persistent)")
            
            # RF params
            print(f"  RfidPower:   {params['RfidPower']} dBm")
            print(f"  Ant:         {params['Ant']}")
            
            # Other
            print(f"  Addr:        0x{params['Addr']:02X}")
            print(f"  RFIDPRO:     {params['RFIDPRO']}")
            print(f"  Interface:   0x{params['Interface']:02X}")
            print(f"  Baudrate:    {params['Baudrate']}")
            print(f"  RfidFreq:    {params['RfidFreq']}")
            print(f"  InquiryArea: {params['InquiryArea']}")
            print(f"  FilterTime:  {params['FilterTime']}")
            print(f"  TriggerTime: {params['TriggerTime']}")
            print(f"  BuzzerTime:  {params['BuzzerTime']}")
            print(f"  PollingInt:  {params['PollingInterval']}")
            print("=" * 50)
    else:
        print(f"   ❌ Failed (Status: {status})")

    conn.close()
    server.close()

if __name__ == "__main__":
    main()
