"""
RFID Reader - Full initialization and inventory sequence.
Based on M-200 manual protocol.
"""
import socket
import struct
import sys
import time
from datetime import datetime

HEAD = 0xCF
BROADCAST_ADDR = 0xFF
PRESET_VALUE = 0xFFFF
POLYNOMIAL = 0x8408

LOG_FILE = "rfid_full_log.txt"
log_file = None

def log(msg):
    print(msg)
    if log_file:
        log_file.write(msg + "\n")
        log_file.flush()

def calculate_crc16(data):
    crc = PRESET_VALUE
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ POLYNOMIAL if crc & 0x0001 else crc >> 1
    return crc

def build_command(cmd, data=b"", addr=BROADCAST_ADDR):
    frame = struct.pack(">BBHB", HEAD, addr, cmd, len(data)) + data
    crc = calculate_crc16(frame)
    frame += struct.pack(">H", crc)
    return frame

def hex_str(data):
    return " ".join(f"{b:02X}" for b in data)

def send_and_recv(sock, cmd_name, cmd_code, data=b"", timeout=5.0):
    """Send command and receive response with full logging."""
    cmd = build_command(cmd_code, data)
    log(f"\n[{cmd_name}] CMD=0x{cmd_code:04X}")
    log(f"  TX: {hex_str(cmd)} ({len(cmd)} bytes)")
    
    try:
        sock.sendall(cmd)
        sock.settimeout(timeout)
        response = sock.recv(1024)
        log(f"  RX: {hex_str(response)} ({len(response)} bytes)")
        
        if len(response) >= 6 and response[0] == HEAD:
            resp_cmd = struct.unpack(">H", response[2:4])[0]
            resp_len = response[4]
            resp_status = response[5]
            log(f"  Parsed: CMD=0x{resp_cmd:04X}, LEN={resp_len}, STATUS=0x{resp_status:02X}")
            
            # Parse tag data if successful inventory
            if resp_status == 0x00 and resp_cmd == 0x0001 and resp_len > 1:
                tag_data = response[6:6+resp_len-1]
                log(f"  TAG DATA: {hex_str(tag_data)}")
                parse_tags(tag_data)
            elif resp_status == 0x12:
                log(f"  --> No tags (inventory complete)")
            elif resp_status == 0x14:
                log(f"  --> Tag timeout")
            
            return response, resp_status
        else:
            log(f"  --> Unexpected response format")
            return response, None
            
    except socket.timeout:
        log(f"  --> TIMEOUT (no response)")
        return None, None
    except Exception as e:
        log(f"  --> ERROR: {e}")
        return None, None

def parse_tags(data):
    """Parse tag data from inventory response."""
    offset = 0
    tag_num = 0
    while offset + 5 <= len(data):
        rssi = data[offset]
        ant = data[offset + 1]
        pc = struct.unpack(">H", data[offset+2:offset+4])[0]
        epc_len = data[offset + 4]
        
        if offset + 5 + epc_len > len(data):
            break
            
        epc = data[offset+5:offset+5+epc_len]
        tag_num += 1
        log(f"  TAG #{tag_num}:")
        log(f"    EPC: {hex_str(epc)}")
        log(f"    RSSI: -{rssi} dBm")
        log(f"    Antenna: {ant}")
        log(f"    PC: 0x{pc:04X}")
        
        offset += 5 + epc_len
    
    if tag_num == 0:
        log("  --> Could not parse tag data")

def main():
    global log_file
    
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    
    log_file = open(LOG_FILE, "w", encoding="utf-8")
    log(f"=== RFID Full Protocol Test - {datetime.now()} ===")
    log(f"Target: {ip}:{port}")
    
    # Connect
    log("\n" + "=" * 60)
    log("CONNECTING")
    log("=" * 60)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((ip, port))
        log(f"[OK] Connected to {ip}:{port}")
    except Exception as e:
        log(f"[FAIL] Connection error: {e}")
        return 1
    
    # Clear buffer
    sock.setblocking(False)
    try:
        buf = sock.recv(4096)
        if buf:
            log(f"Cleared buffer: {hex_str(buf)}")
    except:
        pass
    sock.setblocking(True)
    
    log("\n" + "=" * 60)
    log("STEP 1: Initialize Module (CMD 0x0072)")
    log("=" * 60)
    send_and_recv(sock, "MODULE_INIT", 0x0072)
    time.sleep(0.5)
    
    log("\n" + "=" * 60)
    log("STEP 2: Get Device Info (CMD 0x0070)")
    log("=" * 60)
    send_and_recv(sock, "DEVICE_INFO", 0x0070)
    time.sleep(0.3)
    
    log("\n" + "=" * 60)
    log("STEP 3: Get All Parameters (CMD 0x0052)")
    log("=" * 60)
    send_and_recv(sock, "GET_ALL_PARAMS", 0x0052)
    time.sleep(0.3)
    
    log("\n" + "=" * 60)
    log("STEP 4: Set Power 30dBm (CMD 0x002F)")
    log("=" * 60)
    send_and_recv(sock, "SET_POWER", 0x002F, bytes([30]))
    time.sleep(0.3)
    
    log("\n" + "=" * 60)
    log("STEP 5: Inventory Attempts")
    log("=" * 60)
    
    # Try multiple inventory approaches
    attempts = [
        ("Inventory 1 sec", 0x0001, bytes([0x00, 0x01])),
        ("Inventory 3 sec", 0x0001, bytes([0x00, 0x03])),
        ("Inventory 1 cycle", 0x0001, bytes([0x01, 0x01])),
    ]
    
    found_tags = False
    for name, cmd, data in attempts:
        log(f"\n--- {name} ---")
        response, status = send_and_recv(sock, name, cmd, data, timeout=8.0)
        
        if status == 0x00:
            log("*** TAGS FOUND! ***")
            found_tags = True
            break
        elif status == 0x12:
            log("No tags in range")
        
        # Stop and clear
        send_and_recv(sock, "STOP", 0x0028, timeout=2.0)
        time.sleep(0.5)
    
    log("\n" + "=" * 60)
    log("SUMMARY")
    log("=" * 60)
    if found_tags:
        log("[SUCCESS] Tag(s) detected!")
    else:
        log("[INFO] No tags detected")
        log("- Ensure tag is within 1-2 meters of antenna")
        log("- Check antenna connection")
        log("- Verify tag is UHF RFID (not HF/NFC)")
    
    sock.close()
    log(f"\nFull log saved to: {LOG_FILE}")
    log_file.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
