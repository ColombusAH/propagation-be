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

def drain_socket(client, duration=1.0):
    """Read and discard all data from socket for a duration."""
    end_time = time.time() + duration
    client.settimeout(0.1)
    bytes_read = 0
    try:
        while time.time() < end_time:
            chunk = client.recv(4096)
            if not chunk: break
            bytes_read += len(chunk)
    except socket.timeout:
        pass
    print(f"  [i] Drained {bytes_read} bytes of noise.")
    client.settimeout(5.0) # Restore timeout

def wait_for_response(client, expected_cmd):
    """Loop read until specific CMD response is found."""
    start_time = time.time()
    buffer = b""
    while time.time() - start_time < 5.0:
        try:
            chunk = client.recv(4096)
            if not chunk: return False, "Connection Closed"
            buffer += chunk
            
            while len(buffer) >= 6:
                if buffer[0] != 0xCF:
                     # Scan ahead for header
                     idx = buffer.find(b'\xCF', 1)
                     if idx != -1:
                        buffer = buffer[idx:]
                     else:
                        buffer = b""
                     continue

                length = buffer[4]
                if len(buffer) < 7 + length:
                    break
                
                # Extract Frame
                frame = buffer[:7+length]
                buffer = buffer[7+length:]
                
                cmd = (frame[2] << 8) | frame[3]
                status = frame[5]
                
                if cmd == expected_cmd:
                    return True, status
                elif cmd == 0x0082:
                    continue # Ignore tag reports
                else:
                    print(f"  [i] Ignored unsolicited CMD: 0x{cmd:04X}")
                    
        except socket.timeout:
            return False, "Timeout"
            
    return False, "Timeout Loop"

def configure_reader():
    print(f"=== RFID READER CONFIGURATION (AGGRESSIVE) ===")
    print(f"1. Listening on {LISTEN_IP}:{LISTEN_PORT}...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((LISTEN_IP, LISTEN_PORT))
        server.listen(1)
        print("Waiting for Reader to connect...")
        
        client, addr = server.accept()
        print(f"\n[+] Reader Connected! IP: {addr[0]}")
        
        # 1. Drain initial noise
        print("\n[Step 1] Draining initial traffic...")
        drain_socket(client, duration=2.0)
        
        target_addr = 0xFF # Force Broadcast to ensure it gets it
        
        # 2. Stop Inventory / Init (0x0050)
        print("\n[Step 2] Sending INIT/STOP (0x0050) - Broadcast...")
        cmd_stop = build_command(0x0050, addr=target_addr)
        client.send(cmd_stop)
        
        success, status = wait_for_response(client, 0x0050)
        if success and status == 0x00:
            print("  [+] SUCCESS: Reader Stopped/Initialized.")
        else:
            print(f"  [-] WARNING: Stop failed or no ACK. Status/Error: {status}")
            
        time.sleep(1.0) # Wait for it to really stop

        # 3. Set Query Params (Session 0, Q=4) - With Retry
        print("\n[Step 3] Setting Query Parameters (Session 0, Q=4)...")
        # RFM_SET_QUERY_PARAM = 0x0012
        payload = struct.pack("BBB", 4, 0, 0)
        
        success = False
        for attempt in range(1, 4):
            print(f"  Attempt {attempt}/3...")
            cmd_config = build_command(0x0012, data=payload, addr=target_addr)
            client.send(cmd_config)
            
            # Drain/Wait for specific ACK
            success, status = wait_for_response(client, 0x0012)
            if success and status == 0x00:
                print("  [+] SUCCESS: Reader configured to Session 0 (Continuous) with Q=4.")
                success = True
                break
            else:
                print(f"  [-] Retry: No ACK/Error (Status: {status})")
                time.sleep(0.5)
        
        if not success:
             print("  [-] FAILED: Could not configure reader after 3 attempts.")
        
    except Exception as e:
        print(f"[!] Server Error: {e}")
    finally:
        server.close()
        print("\n=== Configuration Complete ===")

if __name__ == "__main__":
    configure_reader()
