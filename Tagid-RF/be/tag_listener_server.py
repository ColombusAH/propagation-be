"""
=============================================================================
Chafon M-200 Tag Listener - TCP Server Mode (Enhanced)
=============================================================================
The M-200 reader works in PUSH mode - it connects TO YOUR SERVER and sends
tag data when tags are read.

Features:
- TCP server listening for reader connections
- Real-time tag parsing with Stream Buffering (fixes batch packet issues)
- Callback support for external integration
- Log file with all tag events
- Unique tag tracking
- Statistics on connection close

Usage:
    python tag_listener_server.py [port]
    
Example:
    python tag_listener_server.py 4001
    
=============================================================================
"""
import json
import logging
import os
import socket
import struct
import sys
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional, Set, Callable

# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_PORT = 2022  # Changed from 4001 - Gate Reader uses port 2022
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "tag_listener.log")
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 5

# ============================================================================
# GLOBAL CALLBACK
# ============================================================================
_tag_callback: Optional[Callable[[Dict[str, Any]], None]] = None

def set_tag_callback(callback: Callable[[Dict[str, Any]], None]):
    """Set a callback function to be called when a tag is scanned."""
    global _tag_callback
    _tag_callback = callback

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Setup logging with file and console handlers."""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("tag_listener")
    logger.setLevel(logging.DEBUG)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)  # Changed to DEBUG to see raw frames
    console_formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# ============================================================================
# COMMAND CODES
# ============================================================================

COMMANDS = {
    0x0070: "DEVICE_INFO",
    0x0072: "MODULE_INIT",
    0x0082: "GATE_STATUS",  # Tag notification
    0x0063: "WORK_MODE",
    0x0064: "REMOTE_SERVER",
    0x0074: "FILTER_TIME",
    0x0076: "ACCESS_OPERATE",
    0x005F: "GATE_WORK_PARAM",
    0x0080: "GPIO_LEVEL",
    0x0083: "GATE_PARAM",
    0x0084: "EAS_MASK",
}

# ============================================================================
# TAG STORAGE
# ============================================================================

class TagStore:
    """Thread-safe storage for scanned tags."""
    
    def __init__(self, max_tags: int = 1000):
        self._tags: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._max_tags = max_tags
        self._unique_epcs: Set[str] = set()
    
    def add_tag(self, tag_data: Dict[str, Any]) -> bool:
        """Add a tag to the store. Returns True if this is a new EPC."""
        with self._lock:
            epc = tag_data.get("epc", "")
            is_new = epc not in self._unique_epcs
            self._unique_epcs.add(epc)
            
            # Add to history
            self._tags.append(tag_data)
            
            # Trim if too many
            if len(self._tags) > self._max_tags:
                self._tags = self._tags[-self._max_tags:]
            
            return is_new
    
    def get_recent(self, count: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return list(reversed(self._tags[-count:]))
    
    def get_unique_count(self) -> int:
        with self._lock:
            return len(self._unique_epcs)
    
    def get_total_count(self) -> int:
        with self._lock:
            return len(self._tags)
    
    def clear(self):
        with self._lock:
            self._tags.clear()
            self._unique_epcs.clear()

tag_store = TagStore()

# ============================================================================
# PARSER LOGIC
# ============================================================================

def parse_frame(data: bytes) -> Optional[Dict[str, Any]]:
    """Parse a single complete frame."""
    if len(data) < 7:
        return None
    
    head = data[0]
    if head != 0xCF:
        return None
    
    addr = data[1]
    cmd = struct.unpack(">H", data[2:4])[0]
    length = data[4]
    
    result = {
        "head": f"0x{head:02X}",
        "addr": addr,
        "cmd": cmd,
        "cmd_name": COMMANDS.get(cmd, f"UNKNOWN_0x{cmd:04X}"),
        "length": length,
        "raw_hex": data.hex().upper(),
        "timestamp": datetime.now().isoformat(),
    }
    
    # 0x0082 (Active Report), 0x0001 (Inventory Resp), 0x0018 (Cached)
    if cmd == 0x0082 or cmd == 0x0001 or cmd == 0x0018:
        result["type"] = "TAG"
        if len(data) >= 5 + length:
            
            # 0x0082 Format (Heuristic): [Ant (1)][RSSI (1)][...EPC...]
            # Payload starts at data[5]
            if cmd == 0x0082:
                if length >= 2:
                    result["antenna"] = data[5] # Byte 0 of payload
                    result["rssi"] = data[6]    # Byte 1 of payload
                    payload_for_epc = data[7:5+length] 
                else:
                    result["antenna"] = 1
                    result["rssi"] = 0
                    payload_for_epc = data[5:5+length]

            # 0x0001 Format (Standard): [Status(1)][RSSI(1)][Ant(1)][...EPC...]
            elif cmd == 0x0001:
                result["status"] = data[5]
                if length >= 3:
                     result["rssi"] = data[6]
                     result["antenna"] = data[7]
                     payload_for_epc = data[8:5+length]
                else:
                     result["rssi"] = -60
                     result["antenna"] = 1
                     payload_for_epc = data[6:5+length]
            
            else: # Fallback
                result["antenna"] = 1
                result["rssi"] = 0
                payload_for_epc = data[5:5+length]
            
            # Extract EPC
            epc = _extract_epc_from_payload(payload_for_epc)
            result["epc"] = epc if epc else "EMPTY"
            result["epc_length"] = len(epc) // 2 if epc else 0
            
    elif cmd == 0x0070:
        result["type"] = "DEVICE_INFO"
        result["epc"] = None
    elif cmd in COMMANDS:
        result["type"] = "CONFIG"
        result["epc"] = None
    else:
        result["type"] = "UNKNOWN"
        result["epc"] = None
    
    return result



def extract_epcs_from_raw(data: bytes) -> List[str]:
    """Extract EPCs from raw data - looking for E2 80 68 94 pattern (Gate Reader tags)."""
    epcs = []
    
    # The tags all start with E2 80 68 94 (Impinj Monza chip prefix)
    pattern = b'\xE2\x80\x68\x94'
    
    i = 0
    while i < len(data) - 12:
        if data[i:i+4] == pattern:
            # Extract 12-byte EPC
            epc = data[i:i+12].hex().upper()
            if epc not in epcs:
                epcs.append(epc)
            i += 12
        else:
            i += 1
    
    return epcs


def _extract_epc_from_payload(payload: bytes) -> Optional[str]:
    """Extract EPC from payload - first try pattern matching, then fallback to end extraction."""
    if not payload:
        return None
    
    # Method 1: Try pattern-based extraction (E2 80 68 94 prefix)
    epcs = extract_epcs_from_raw(payload)
    if epcs:
        return epcs[0]  # Return first found EPC
    
    # Method 2: Fallback - Find non-zero bytes from the end
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

def process_buffer(buffer: bytes) -> tuple[bytes, List[Dict[str, Any]]]:
    """
    Process buffer and extract all complete frames.
    Returns: (remaining_buffer, list_of_results)
    """
    results = []
    
    while len(buffer) >= 7:
        # Find Header 0xCF
        if buffer[0] != 0xCF:
            # Shift buffer until next 0xCF or empty
            try:
                idx = buffer.index(0xCF)
                buffer = buffer[idx:]
            except ValueError:
                buffer = b""
                break
        
        # Now buffer[0] is 0xCF
        if len(buffer) < 7:
            break
            
        length_byte = buffer[4]
        frame_total_len = 7 + length_byte
        
        if len(buffer) < frame_total_len:
            # Need more data
            break
            
        # Extract full frame
        frame_data = buffer[:frame_total_len]
        buffer = buffer[frame_total_len:]
        
        # Parse it
        try:
            res = parse_frame(frame_data)
            if res:
                results.append(res)
        except Exception as e:
            logger.error(f"Error parsing frame: {e}")
            
    return buffer, results

# ============================================================================
# ACTIVE CONTROL (For Answer Mode)
# ============================================================================

_active_client: Optional[socket.socket] = None
_client_lock = threading.Lock()

def calculate_crc16(data: bytes) -> int:
    """Calculate CRC16 (Polynomial 0x8408)."""
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

def build_command(cmd_code: int, data: bytes = b"") -> bytes:
    """Build a command frame with CRC."""
    # Head(1) + Addr(1) + Cmd(2) + Len(1) + Data(N) + CRC(2)
    # Default Address = 0xFF (Broadcast) to ensure response from any connected reader
    head = 0xCF
    addr = 0xFF
    
    frame_body = struct.pack(">BBBB", head, addr, (cmd_code >> 8) & 0xFF, cmd_code & 0xFF)
    frame_body += struct.pack("B", len(data))
    frame_body += data
    
    # Calculate CRC over the whole frame body
    crc = calculate_crc16(frame_body)
    
    # FIXED: Big Endian CRC (>H) per M-200 Manual
    return frame_body + struct.pack(">H", crc)

# Global state for reader mode
_reader_mode = "ACTIVE" # Default, assumes we need to poll

def send_command_to_active_client(cmd_code: int, data: bytes = b"") -> bool:
    """Send a command to the currently connected reader."""
    global _active_client, _reader_mode
    
    with _client_lock:
        if not _active_client:
            logger.warning("No reader connected to send command")
            return False
            
        try:
            # PASSIVE MODE PROTECTION
            if _reader_mode == "PASSIVE" and cmd_code == 0x0001:
                logger.info("Reader is in PASSIVE mode (sending tags automatically). Skipping Start Inventory command.")
                return True
                
            frame = build_command(cmd_code, data)
            _active_client.send(frame)
            logger.info(f"Sent Command 0x{cmd_code:04X} to reader")
            return True
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            _active_client = None # Assume disconnected
            return False

def start_inventory():
    """Send Start Inventory (Continuous) command."""
    # RFM_INVENTORYISO_CONTINUE = 0x0001
    # Payload: 0x00 (TimeMode) + 0x00 (Param=0 -> Continuous)
    return send_command_to_active_client(0x0001, data=b'\x00\x00')

def stop_inventory():
    """Send Stop Inventory command."""
    # RFM_INVENTORY_STOP = 0x0028
    return send_command_to_active_client(0x0028)

# ============================================================================
# CONNECTION HANDLER
# ============================================================================

def handle_client(client_socket: socket.socket, client_address: tuple):
    global _active_client, _reader_mode
    
    reader_ip = client_address[0]
    reader_port = client_address[1]
    
    logger.info("=" * 50)
    logger.info(f"Reader connected: {reader_ip}:{reader_port}")
    logger.info("=" * 50)
    
    # Register as active client
    with _client_lock:
        _active_client = client_socket
    
    tag_count = 0
    buffer = b""
    connection_start = datetime.now()
    
    try:
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                logger.info("Reader disconnected (closed connection)")
                break
            
            buffer += chunk
            
            # Log raw chunk for debugging (first 50 chars)
            logger.debug(f"Received {len(chunk)} bytes. Raw: {chunk.hex().upper()[:50]}...")
            
            # Process buffer with stream logic
            buffer, parsed_frames = process_buffer(buffer)
            
            if len(parsed_frames) > 0:
                logger.debug(f"Processed {len(parsed_frames)} frames from buffer. Remaining: {len(buffer)} bytes")
            
            for result in parsed_frames:
                frame_type = result.get("type", "UNKNOWN")
                cmd = result.get("cmd", 0)
                
                # Auto-Detect Passive Mode
                if cmd == 0x0082 and _reader_mode != "PASSIVE":
                    _reader_mode = "PASSIVE"
                    logger.info("!!! AUTO-DETECTED PASSIVE MODE (Receiving 0x0082 frames) !!!")
                    logger.info("Disabling automatic 'Start Inventory' commands.")
                
                if frame_type == "TAG":
                    epc = result.get("epc", "")
                    if epc and epc != "EMPTY":
                        tag_count += 1
                        tag_data = {
                            "epc": epc,
                            "epc_length": result.get("epc_length", 0),
                            "timestamp": result.get("timestamp"),
                            "reader_ip": reader_ip,
                            "raw": result.get("raw_hex"),
                            "rssi": result.get("rssi", -60),
                            "antenna": result.get("antenna", 1),
                        }
                        
                        # Add to local store
                        is_new = tag_store.add_tag(tag_data)
                        
                        # Log
                        status_str = "NEW" if is_new else "SEEN"
                        logger.info(f"*** {status_str} TAG *** EPC: {epc}")
                        
                        # Trigger Callback (Critical for WebSocket)
                        if _tag_callback:
                            try:
                                _tag_callback(tag_data)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                                
    except ConnectionResetError:
        logger.warning("Connection reset by reader")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        with _client_lock:
            if _active_client == client_socket:
                _active_client = None
        client_socket.close()

# ============================================================================
# SERVER
# ============================================================================

def start_server(port: int = DEFAULT_PORT):
    listen_ip = "0.0.0.0"
    print(f"Server starting on {listen_ip}:{port}")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((listen_ip, port))
        server.listen(5)
        logger.info(f"Server listening on {listen_ip}:{port}")
        
        while True:
            client, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(client, addr), daemon=True)
            t.start()
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.close()

# API Exports
def get_recent_tags(count: int = 50) -> List[Dict[str, Any]]:
    return tag_store.get_recent(count)

def get_tag_stats() -> Dict[str, Any]:
    return {
        "total_scans": tag_store.get_total_count(),
        "unique_epcs": tag_store.get_unique_count(),
    }

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    start_server(port)
