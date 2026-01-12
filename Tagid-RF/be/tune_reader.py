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

def print_params(data):
    """Print parameter breakdown"""
    if len(data) < 25:
        return
    
    print(f"   Addr:           0x{data[0]:02X}")
    print(f"   RFIDPRO:        {data[1]}")
    
    work_modes = {0: "Answer", 1: "Active", 2: "Trigger"}
    print(f"   WorkMode:       {data[2]} ({work_modes.get(data[2], '?')})")
    
    print(f"   Interface:      0x{data[3]:02X}")
    print(f"   Baudrate:       {data[4]}")
    print(f"   WGSet:          {data[5]}")
    print(f"   Ant:            {data[6]}")
    print(f"   RfidFreq:       {data[7:15].hex().upper()}")
    print(f"   RfidPower:      {data[15]} dBm ⭐")
    print(f"   InquiryArea:    {data[16]}")
    print(f"   QValue:         {data[17]} ⭐")
    print(f"   Session:        {data[18]} ⭐")
    print(f"   AcsAddr:        {data[19]}")
    print(f"   AcsDataLen:     {data[20]}")
    print(f"   FilterTime:     {data[21]} ⭐")
    print(f"   TriggerTime:    {data[22]}")
    print(f"   BuzzerTime:     {data[23]}")
    print(f"   PollingInt:     {data[24]}")

def main():
    print("=== TUNE READER (Sensitivity & Timing) ===")
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
    else: print("   ⚠️ Stop Failed (continuing anyway).")
    
    time.sleep(1.0)
    
    # 2. Read Current Params
    print("\n2. Reading Current Params (0x0072)...")
    conn.send(build_command(0x0072))
    success, status, data = wait_for_response(conn, 0x0072)
    
    if not success or not data:
        print(f"   ❌ Failed to read params.")
        conn.close()
        server.close()
        return
    
    print(f"   ✅ Current Params:")
    print_params(data)
    
    time.sleep(0.5)
    
    # 3. Modify Params for maximum sensitivity
    print("\n3. Tuning for Maximum Sensitivity...")
    new_params = bytearray(data)
    
    # Changes for better detection:
    # Byte 2: WorkMode = 1 (Active)
    new_params[2] = 0x01
    print("   🔧 WorkMode: 1 (Active)")
    
    # Byte 15: RfidPower = 0x1E (30 dBm max safe) or keep at 0x21 (33)
    # Keep at 0x21 for max power
    print(f"   🔧 RfidPower: {new_params[15]} dBm (unchanged)")
    
    # Byte 17: QValue = 7 (better for 16+ tags, more slots)
    new_params[17] = 0x07
    print("   🔧 QValue: 7 (increased for 16+ tags)")
    
    # Byte 18: Session = 0 (continuous, no persistence)
    new_params[18] = 0x00
    print("   🔧 Session: 0 (continuous)")
    
    # Byte 21: FilterTime = 0 (no filtering delay)
    new_params[21] = 0x00
    print("   🔧 FilterTime: 0 (no delay)")
    
    # Byte 22: TriggerTime = 0 (immediate trigger)
    new_params[22] = 0x00
    print("   🔧 TriggerTime: 0 (immediate)")
    
    # Byte 24: PollingInterval = 0 (fastest polling)
    new_params[24] = 0x00
    print("   🔧 PollingInterval: 0 (fastest)")
    
    print(f"\n   📝 New Params: {bytes(new_params).hex().upper()}")
    
    # 4. Set New Params
    print("\n4. Applying New Params (0x0071)...")
    conn.send(build_command(0x0071, bytes(new_params)))
    success, status, _ = wait_for_response(conn, 0x0071)
    
    if success and status == 0x00:
        print("   ✅ SUCCESS! Params Updated.")
    else:
        print(f"   ❌ Failed (Status: {status})")

    time.sleep(0.5)

    # 5. Verify
    print("\n5. Verifying New Params (0x0072)...")
    conn.send(build_command(0x0072))
    success, status, data = wait_for_response(conn, 0x0072)
    
    if success and data:
        print("   ✅ New Params:")
        print_params(data)
    else:
        print("   ⚠️ Verify Failed.")

    print("\n6. Power cycle the reader and run proper_inventory.py!")
    
    conn.close()
    server.close()

if __name__ == "__main__":
    main()
