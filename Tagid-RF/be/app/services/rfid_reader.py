"""
RFID Reader Service for Chafon M-200 Gate Reader

This service handles connection and communication with the M-200 UHF RFID reader
using its native protocol (not compatible with standard CF-RU readers).

Based on: CF-M Gate Reader User Manual V1.2
"""

import asyncio
import logging
import socket
import struct
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from app.core.config import get_settings
from app.models.rfid_tag import RFIDReaderConfig, RFIDScanHistory, RFIDTag
from app.routers.websocket import manager
from app.services.database import SessionLocal
from app.services.m200_protocol import (  # noqa: F401 - Full protocol API exposed for comprehensive reader control
    HEAD,
    M200Command,
    M200Commands,
    M200ResponseParser,
    M200Status,
    build_get_all_params_command,
    build_get_device_info_command,
    build_get_gate_param_command,
    build_get_gate_status_command,
    build_get_gpio_levels_command,
    build_get_gpio_param_command,
    build_get_network_command,
    build_get_query_param_command,
    build_inventory_command,
    build_module_init_command,
    build_read_tag_command,
    build_relay1_command,
    build_relay2_command,
    build_select_tag_command,
    build_set_all_params_command,
    build_set_gate_param_command,
    build_set_gpio_param_command,
    build_set_network_command,
    build_set_power_command,
    build_set_query_param_command,
    build_set_rssi_filter_command,
    build_stop_inventory_command,
    build_write_tag_command,
    parse_device_info,
    parse_gate_status,
    parse_gpio_levels,
    parse_inventory_response,
    parse_network_response,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class RFIDReaderService:
    """Service for managing M-200 RFID reader connection and operations."""

    def __init__(self):
        # Default settings from env/config (fallback)
        self.reader_ip = getattr(settings, "RFID_READER_IP", "192.168.1.100")
        self.reader_port = getattr(settings, "RFID_READER_PORT", 4001)
        self.socket_timeout = getattr(settings, "RFID_SOCKET_TIMEOUT", 10)
        self.reader_id = getattr(settings, "RFID_READER_ID", "M-200")

        self.power_level = 26
        self.antenna_mask = 1

        self.is_connected = False
        self.is_scanning = False

        self._socket: Optional[socket.socket] = None
        self._scan_task: Optional[asyncio.Task] = None
        self._device_info: Optional[Dict[str, Any]] = None

        # Load from DB if available
        try:
            self.load_config_from_db()
        except Exception as e:
            logger.warning(f"Could not load RFID config from DB: {e}. Using defaults.")

    def load_config_from_db(self):
        """Load configuration from database."""
        db = SessionLocal()
        try:
            config = db.query(RFIDReaderConfig).filter(RFIDReaderConfig.reader_id == self.reader_id).first()
            if config:
                self.reader_ip = config.ip_address
                self.reader_port = config.port
                self.power_level = config.power_dbm
                self.antenna_mask = config.antenna_mask
                logger.info(f"✓ Loaded RFID reader config from DB: {self.reader_ip}:{self.reader_port}")
            else:
                # Create default config in DB
                new_config = RFIDReaderConfig(
                    reader_id=self.reader_id,
                    ip_address=self.reader_ip,
                    port=self.reader_port,
                    power_dbm=self.power_level,
                    antenna_mask=self.antenna_mask
                )
                db.add(new_config)
                db.commit()
                logger.info(f"✓ Created default RFID reader config in DB for {self.reader_id}")
        finally:
            db.close()

    def save_config_to_db(self, **kwargs):
        """Save current or specific configuration to database."""
        db = SessionLocal()
        try:
            config = db.query(RFIDReaderConfig).filter(RFIDReaderConfig.reader_id == self.reader_id).first()
            if not config:
                config = RFIDReaderConfig(reader_id=self.reader_id)
                db.add(config)
            
            # Update fields
            if "ip" in kwargs: config.ip_address = kwargs["ip"]
            if "port" in kwargs: config.port = kwargs["port"]
            if "power" in kwargs: config.power_dbm = kwargs["power"]
            if "antenna_mask" in kwargs: config.antenna_mask = kwargs["antenna_mask"]
            
            db.commit()
            logger.info(f"✓ Saved RFID reader config to DB for {self.reader_id}")
        finally:
            db.close()

    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return {
            "is_connected": self.is_connected,
            "is_scanning": self.is_scanning,
            "reader_ip": self.reader_ip,
            "reader_port": self.reader_port,
            "power_level": self.power_level,
            "antenna_mask": self.antenna_mask,
            "device_info": self._device_info,
        }

    # Aliases for compatibility with tests and API usage
    async def get_all_config(self) -> Dict[str, Any]:
        """Alias for get_all_params."""
        return await self.get_all_params()

    async def set_network(self, ip: str, subnet: str, gateway: str, port: int) -> bool:
        """Alias for set_network_config."""
        return await self.set_network_config(ip, subnet, gateway, port)

    def send_command(self, command: M200Command) -> bytes:
        """Alias for _send_command (for tests)."""
        return self._send_command(command)

    async def connect(self) -> bool:
        """
        Connect to M-200 via TCP/IP.

        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            logger.info("Already connected to M-200 reader")
            return True

        try:
            logger.info(f"Connecting to M-200 at {self.reader_ip}:{self.reader_port}")

            # Create TCP socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.socket_timeout)
            self._socket.connect((self.reader_ip, self.reader_port))

            self.is_connected = True
            logger.info(f"✓ Connected to M-200 at {self.reader_ip}:{self.reader_port}")

            # Small delay to let device stabilize
            await asyncio.sleep(0.1)

            # Clear any buffered/unsolicited messages
            self._socket.setblocking(False)
            try:
                buffered = self._socket.recv(4096)
                if buffered:
                    logger.debug(
                        f"Cleared {len(buffered)} bytes of buffered data: {buffered.hex().upper()}"
                    )
            except BlockingIOError:
                pass  # No data buffered
            finally:
                self._socket.setblocking(True)
                self._socket.settimeout(self.socket_timeout)

            # Get device info to verify connection
            device_info = await self.get_reader_info()
            if device_info.get("connected"):
                self._device_info = device_info
                logger.info(
                    f"✓ M-200 connection verified. Model: {device_info.get('model', 'Unknown')}, SN: {device_info.get('rfid_serial_number', 'Unknown')}"
                )
            else:
                logger.warning("! Connected but could not retrieve device info - reader might be busy")

            return True

        except socket.timeout:
            logger.error(f"Connection timeout to {self.reader_ip}:{self.reader_port}")
            self.is_connected = False
            return False
        except ConnectionRefusedError:
            logger.error(f"Connection refused by {self.reader_ip}:{self.reader_port}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.exception(f"Connection failed: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Disconnect from M-200 reader."""
        if self.is_scanning:
            await self.stop_scanning()

        if not self.is_connected:
            logger.info("Already disconnected from M-200")
            return

        try:
            if self._socket:
                self._socket.close()
                self._socket = None
            logger.info("✓ Disconnected from M-200")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}", exc_info=True)
        finally:
            self.is_connected = False
            self._device_info = None

    def _send_command(self, command: M200Command, max_retries: int = 3) -> bytes:
        """
        Send command to M-200 and receive response.

        Handles unsolicited messages by reading until we get a response matching our command.

        Frame format: [HEAD][ADDR][CMD_H][CMD_L][LEN][STATUS][DATA...][CRC_L][CRC_H]

        Args:
            command: M200Command to send
            max_retries: Maximum number of responses to read looking for matching CMD

        Returns:
            Raw response bytes matching our command

        Raises:
            ConnectionError: If not connected
            socket.timeout: If read/write timeout
        """
        if not self.is_connected or not self._socket:
            raise ConnectionError("Not connected to M-200 reader")

        # Send command
        cmd_bytes = command.serialize()
        logger.debug(f"→ TX: {cmd_bytes.hex().upper()} (CMD=0x{command.cmd:04X})")
        self._socket.sendall(cmd_bytes)

        # Receive response - may need to read multiple messages if device sends unsolicited data
        for attempt in range(max_retries):
            response = b""
            header_size = 6

            try:
                # Read at least 1 byte to see what we get
                self._socket.settimeout(1.0)
                first_chunk = self._socket.recv(1)
                if not first_chunk:
                    raise ConnectionError("Connection closed by M-200")
                response += first_chunk

                # If first byte is not 0xCF, might be different protocol - read what we can
                if first_chunk[0] != HEAD:
                    logger.warning(
                        f"Unexpected first byte: 0x{first_chunk[0]:02X} (expected 0x{HEAD:02X})"
                    )
                    # Try to read more with short timeout
                    try:
                        additional = self._socket.recv(1024)
                        if additional:
                            response += additional
                    except socket.timeout:
                        pass  # No more data available
                    # Return what we got - let parser handle the error
                    logger.debug(f"← RX: {response.hex().upper()} (len={len(response)})")
                    return response

                # Restore original timeout
                self._socket.settimeout(self.socket_timeout)

                # Read remaining header bytes
                while len(response) < header_size:
                    chunk = self._socket.recv(header_size - len(response))
                    if not chunk:
                        raise ConnectionError("Connection closed by M-200")
                    response += chunk

                # Parse header to get data length (byte 4, after HEAD, ADDR, CMD_H, CMD_L)
                if len(response) < 5:
                    raise ValueError(f"Response too short: {len(response)} bytes")
                data_len = response[4]

                # Calculate remaining bytes: DATA + CRC(2)
                # data_len (LEN) includes STATUS byte, which is already read in header_size=6
                remaining = data_len - 1 + 2
                while remaining > 0:
                    chunk = self._socket.recv(remaining)
                    if not chunk:
                        raise ConnectionError("Connection closed by M-200")
                    response += chunk
                    remaining -= len(chunk)

                # Check if this response matches our command
                response_cmd = struct.unpack(">H", response[2:4])[0]

                logger.debug(
                    f"← RX: {response.hex().upper()} (len={len(response)}, CMD=0x{response_cmd:04X})"
                )

                if response_cmd == command.cmd:
                    # This is the response we're looking for!
                    return response
                else:
                    # Unsolicited message - log and try again
                    logger.warning(
                        f"Unsolicited message: CMD=0x{response_cmd:04X} (expected 0x{command.cmd:04X}), ignoring and reading next message"
                    )
                    continue

            except socket.timeout:
                # If we got some data, return it for analysis
                if response:
                    logger.warning(f"Read timeout, but got {len(response)} bytes")
                    return response
                # No data on last retry
                if attempt == max_retries - 1:
                    raise
                continue

        # Exhausted retries without finding matching response
        logger.error(f"No matching response found after {max_retries} attempts")
        raise socket.timeout("No matching response received")

    async def get_reader_info(self) -> Dict[str, Any]:
        """
        Get M-200 device information.

        Returns:
            Dictionary with device info
        """
        if not self.is_connected:
            return {"connected": False}

        try:
            # Build and send get device info command
            cmd = build_get_device_info_command()
            response_bytes = await asyncio.to_thread(self._send_command, cmd)

            # Parse response (use lenient CRC checking - device may use proprietary variant)
            try:
                response = M200ResponseParser.parse(response_bytes, strict_crc=False)

                # Check if response CMD matches (some devices send unsolicited messages)
                if response.cmd != M200Commands.RFM_GET_DEVICE_INFO:
                    logger.warning(
                        f"Response CMD mismatch: expected 0x{M200Commands.RFM_GET_DEVICE_INFO:04X}, got 0x{response.cmd:04X}"
                    )
                    logger.warning(
                        "This might be an unsolicited message or different protocol variant"
                    )
                    # Continue anyway - might still have valid data

            except ValueError as e:
                # Protocol mismatch - check if it's JSON/HTTP instead of binary
                response_text = response_bytes.decode("ascii", errors="replace")

                # Detect JSON/HTTP protocol
                if response_text.startswith("Content-Length:") or response_text.startswith("HTTP/"):
                    logger.error(
                        "⚠️  Protocol mismatch: Reader is responding with JSON/HTTP, not binary M-200 protocol"
                    )
                    logger.error(
                        f"This port ({self.reader_port}) appears to be a debug/HTTP port, not the RFID data port"
                    )
                    logger.error(f"Response preview: {response_text[:200]}...")

                    # Try to parse JSON to see what it is
                    try:
                        import json

                        # Extract JSON from Content-Length format
                        if "Content-Length:" in response_text:
                            parts = response_text.split("\r\n\r\n")
                            for part in parts:
                                if part.strip().startswith("{"):
                                    json_data = json.loads(part.strip())
                                    logger.error(
                                        f"JSON response type: {json_data.get('type', 'unknown')}"
                                    )
                                    if json_data.get("type") == "event" and "debugpy" in str(
                                        json_data
                                    ):
                                        logger.error(
                                            "This appears to be a Python debugger port (debugpy), not the RFID reader!"
                                        )
                    except Exception:
                        pass

                    return {
                        "connected": True,
                        "error": f"Wrong protocol: Port {self.reader_port} uses JSON/HTTP, not binary M-200 protocol. This may be a debug/HTTP port. Try a different port (e.g., 4001, 6000, 27011).",
                        "protocol_detected": "JSON/HTTP",
                        "suggested_ports": [4001, 6000, 27011, 2022],
                    }

                # Other protocol mismatch
                logger.error(f"Protocol parsing error: {e}")
                logger.error(
                    f"Raw response ({len(response_bytes)} bytes): {response_bytes.hex().upper()}"
                )
                logger.error(f"Response as ASCII: {repr(response_text)}")
                return {
                    "connected": True,
                    "error": str(e),
                    "raw_response_hex": response_bytes.hex().upper(),
                    "raw_response_ascii": repr(response_text),
                    "raw_response_length": len(response_bytes),
                }

            if not response.success:
                logger.error(
                    f"Get device info failed: {M200Status.get_description(response.status)}"
                )
                return {
                    "connected": True,
                    "error": M200Status.get_description(response.status),
                }

            # Parse device info
            info = parse_device_info(response.data)
            info.update(
                {
                    "connected": True,
                    "ip": self.reader_ip,
                    "port": self.reader_port,
                    "reader_id": self.reader_id,
                }
            )

            logger.info(
                f"Device info: {info.get('reader_type')} v{info.get('rfid_firmware_version')}"
            )
            return info

        except socket.timeout:
            logger.error("Timeout getting reader info")
            return {
                "connected": True,
                "error": "Timeout - device not responding",
            }
        except Exception as e:
            logger.exception(f"Error getting reader info: {e}")
            return {
                "connected": True,
                "error": str(e),
            }

    async def read_single_tag(self) -> List[Dict[str, Any]]:
        """
        Read tags using single inventory cycle.

        Returns:
            List of tag data dictionaries
        """
        if not self.is_connected:
            logger.error("Cannot read tags: not connected")
            return []

        try:
            # Build inventory command (1 cycle, non-continuous)
            cmd = build_inventory_command(inv_type=0x01, inv_param=1)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)

            # Parse response (use lenient CRC checking - device may use proprietary variant)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)

            if response.status == M200Status.INVENTORY_COMPLETE:
                # No tags found
                return []

            if not response.success:
                logger.warning(f"Inventory failed: {M200Status.get_description(response.status)}")
                return []

            # Parse tag data
            tags = parse_inventory_response(response.data)

            if tags:
                logger.info(f"Read {len(tags)} tag(s)")
                for tag in tags:
                    logger.debug(
                        f"  Tag: EPC={tag['epc']}, RSSI={tag['rssi']}dBm, Ant={tag['antenna_port']}"
                    )

            # Add timestamp to each tag
            timestamp = datetime.now(timezone.utc).isoformat()
            for tag in tags:
                tag["timestamp"] = timestamp

            return tags

        except socket.timeout:
            logger.warning("Timeout reading tags")
            return []
        except Exception as e:
            logger.error(f"Error reading tags: {e}", exc_info=True)
            return []

    async def start_scanning(self, callback: Optional[Callable] = None):
        """
        Start continuous tag scanning.

        Args:
            callback: Optional callback function for each tag
        """
        if not self.is_connected:
            logger.error("Cannot start scanning: not connected")
            return

        if self.is_scanning:
            logger.warning("Scanning already in progress")
            return

        self.is_scanning = True
        logger.info("▶ Starting continuous tag scanning loop...")

        self._scan_task = asyncio.create_task(self._scan_loop(callback))

    async def _scan_loop(self, callback: Optional[Callable] = None):
        """Main scanning loop."""
        while self.is_scanning and self.is_connected:
            try:
                # Read tags
                tags = await self.read_single_tag()
                print(tags)
                # Process each tag
                for tag_data in tags:
                    await self._process_tag(tag_data, callback)

                # Small delay between scans
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                logger.info("Scan loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scan loop: {e}", exc_info=True)
                await asyncio.sleep(1)  # Wait before retrying

    async def _process_tag(self, tag_data: Dict[str, Any], callback: Optional[Callable] = None):
        """
        Process a scanned tag: save to DB and broadcast via WebSocket.

        Args:
            tag_data: Tag information dictionary
            callback: Optional callback function
        """
        try:
            db = SessionLocal()
            try:
                epc = tag_data["epc"]

                # Find or create tag
                existing_tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()

                if existing_tag:
                    # Update existing tag
                    existing_tag.read_count += 1
                    existing_tag.last_seen = datetime.now(timezone.utc)
                    existing_tag.rssi = tag_data.get("rssi")
                    existing_tag.antenna_port = tag_data.get("antenna_port")
                    db.commit()
                    db.refresh(existing_tag)
                    tag_id = existing_tag.id
                else:
                    # Create new tag
                    new_tag = RFIDTag(
                        epc=epc,
                        rssi=tag_data.get("rssi"),
                        antenna_port=tag_data.get("antenna_port"),
                        pc=tag_data.get("pc"),
                        location=None,  # Set manually
                    )
                    db.add(new_tag)
                    db.commit()
                    db.refresh(new_tag)
                    tag_id = new_tag.id

                # Create scan history
                history = RFIDScanHistory(
                    epc=epc,
                    rssi=tag_data.get("rssi"),
                    antenna_port=tag_data.get("antenna_port"),
                    reader_id=self.reader_id,
                    scanned_at=datetime.now(timezone.utc),
                )
                db.add(history)
                db.commit()

                # Check for existing mapping
                from app.db.prisma import prisma_client

                encryption_status = {"is_mapped": False, "target_qr": None}

                # Use Prisma to check for mapping
                try:
                    mapping = await prisma_client.client.tagmapping.find_unique(where={"epc": epc})

                    if mapping:
                        encryption_status = {
                            "is_mapped": True,
                            "target_qr": mapping.encryptedQr,  # Note casing from Prisma
                        }
                except Exception as e:
                    logger.error(f"Error checking tag mapping: {e}")

                # Broadcast via WebSocket
                await manager.broadcast(
                    {
                        "type": "tag_scanned",
                        "data": {
                            "tag_id": tag_id,
                            "epc": epc,
                            "rssi": tag_data.get("rssi"),
                            "antenna_port": tag_data.get("antenna_port"),
                            "timestamp": tag_data.get("timestamp"),
                            **encryption_status,
                        },
                    }
                )

                # Call callback if provided
                if callback:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(tag_data)
                    else:
                        callback(tag_data)

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error processing tag: {e}", exc_info=True)

    async def stop_scanning(self):
        """Stop continuous scanning."""
        if not self.is_scanning:
            logger.info("Scanning not active")
            return

        self.is_scanning = False

        # Cancel scan task
        if self._scan_task:
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass
            self._scan_task = None

        # Send stop inventory command if connected
        if self.is_connected:
            try:
                cmd = build_stop_inventory_command()
                await asyncio.to_thread(self._send_command, cmd)
                logger.info("Sent stop inventory command to M-200")
            except Exception as e:
                logger.warning(f"Could not send stop command: {e}")

        logger.info("✓ Stopped tag scanning")

    async def write_tag(
        self, epc: str, bank: int, start_addr: int, data: bytes
    ) -> bool:
        """
        Write data to RFID tag.

        Args:
            epc: Tag EPC to write to
            bank: Memory bank (0=Reserved, 1=EPC, 2=TID, 3=User)
            start_addr: Starting address in words
            data: Binary data to write

        Returns:
            True if successful
        """
        if not self.is_connected:
            return False

        try:
            # 1. Select the tag first
            selected = await self.select_tag(epc)
            if not selected:
                logger.error(f"Failed to select tag {epc} for writing")
                return False

            # 2. Send write command
            cmd = build_write_tag_command(bank, start_addr, data)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)

            if response.success:
                logger.info(f"✓ Successfully wrote data to tag {epc}")
                return True
            else:
                error_desc = M200Status.get_description(response.status)
                logger.error(f"Failed to write to tag {epc}: {error_desc}")
                return False
        except Exception as e:
            logger.error(f"Error writing to tag {epc}: {e}")
            return False

    # =========================================================================
    # HIGH PRIORITY - Module Control
    # =========================================================================

    async def initialize_device(self) -> bool:
        """Initialize/reset the M-200 device."""
        if not self.is_connected:
            return False
        try:
            cmd = build_module_init_command()
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            return response.success
        except Exception as e:
            logger.error(f"Failed to initialize device: {e}")
            return False

    async def set_power(self, power_dbm: int) -> bool:
        """Set RF output power (0-30 dBm)."""
        if not self.is_connected:
            return False
        try:
            cmd = build_set_power_command(power_dbm)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            if response.success:
                self.power_level = power_dbm
                self.save_config_to_db(power=power_dbm)
                logger.info(f"Set RF power to {power_dbm} dBm")
            return response.success
        except Exception as e:
            logger.error(f"Failed to set power: {e}")
            return False

    async def read_tag_memory(
        self, mem_bank: int, start_addr: int, word_count: int
    ) -> Optional[bytes]:
        """
        Read tag memory.

        Args:
            mem_bank: 0=Reserved, 1=EPC, 2=TID, 3=User
            start_addr: Starting word address
            word_count: Number of 16-bit words to read
        """
        if not self.is_connected:
            return None
        try:
            cmd = build_read_tag_command(mem_bank, start_addr, word_count)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            if response.success:
                return response.data
            return None
        except Exception as e:
            logger.error(f"Failed to read tag memory: {e}")
            return None

    # =========================================================================
    # MEDIUM PRIORITY - Configuration
    # =========================================================================

    async def get_network_config(self) -> Dict[str, Any]:
        """Get current network configuration."""
        if not self.is_connected:
            return {"error": "Not connected"}
        try:
            cmd = build_get_network_command()
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            if response.success:
                return parse_network_response(response.data)
            return {"error": M200Status.get_description(response.status)}
        except Exception as e:
            return {"error": str(e)}

    async def set_network_config(
        self,
        ip: str,
        subnet: str = "255.255.255.0",
        gateway: str = "192.168.1.1",
        port: int = 4001,
    ) -> bool:
        """Set network configuration."""
        if not self.is_connected:
            return False
        try:
            cmd = build_set_network_command(ip, subnet, gateway, port)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            if response.success:
                self.reader_ip = ip
                self.reader_port = port
                self.save_config_to_db(ip=ip, port=port)
            return response.success
        except Exception as e:
            logger.error(f"Failed to set network: {e}")
            return False

    async def set_rssi_filter(self, antenna: int, threshold: int) -> bool:
        """Set RSSI threshold for antenna."""
        if not self.is_connected:
            return False
        try:
            cmd = build_set_rssi_filter_command(antenna, threshold)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            return response.success
        except Exception as e:
            logger.error(f"Failed to set RSSI filter: {e}")
            return False

    async def get_all_params(self) -> Dict[str, Any]:
        """Get all device parameters."""
        if not self.is_connected:
            return {"error": "Not connected"}
        try:
            cmd = build_get_all_params_command()
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            return {"success": response.success, "data": response.data.hex().upper()}
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # GPIO Control
    # =========================================================================

    async def get_gpio_levels(self) -> Dict[str, int]:
        """Get current GPIO pin levels."""
        if not self.is_connected:
            return {}
        try:
            cmd = build_get_gpio_levels_command()
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            if response.success:
                return parse_gpio_levels(response.data)
            return {}
        except Exception as e:
            logger.error(f"Failed to get GPIO levels: {e}")
            return {}

    async def set_gpio(self, pin: int, direction: int, level: int = 0) -> bool:
        """Configure GPIO pin."""
        if not self.is_connected:
            return False
        try:
            cmd = build_set_gpio_param_command(pin, direction, level)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            return response.success
        except Exception as e:
            logger.error(f"Failed to set GPIO: {e}")
            return False

    # =========================================================================
    # Relay Control
    # =========================================================================

    async def control_relay(self, relay_num: int, close: bool = True) -> bool:
        """Control relay 1 or 2."""
        if not self.is_connected:
            return False
        try:
            if relay_num == 1:
                cmd = build_relay1_command(close)
            elif relay_num == 2:
                cmd = build_relay2_command(close)
            else:
                logger.error(f"Invalid relay number: {relay_num}")
                return False

            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            if response.success:
                logger.info(f"Relay {relay_num} {'closed' if close else 'opened'}")
            return response.success
        except Exception as e:
            logger.error(f"Failed to control relay: {e}")
            return False

    # =========================================================================
    # Gate Control
    # =========================================================================

    async def get_gate_status(self) -> Dict[str, Any]:
        """Get gate detection status."""
        if not self.is_connected:
            return {"error": "Not connected"}
        try:
            cmd = build_get_gate_status_command()
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            if response.success:
                return parse_gate_status(response.data)
            return {"error": M200Status.get_description(response.status)}
        except Exception as e:
            return {"error": str(e)}

    async def set_gate_config(
        self, mode: int = 1, sensitivity: int = 80, direction_detect: bool = True
    ) -> bool:
        """Configure gate detection mode."""
        if not self.is_connected:
            return False
        try:
            cmd = build_set_gate_param_command(mode, sensitivity, direction_detect)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            return response.success
        except Exception as e:
            logger.error(f"Failed to set gate config: {e}")
            return False

    # =========================================================================
    # Query & Select Commands
    # =========================================================================

    async def set_query_params(self, q_value: int = 4, session: int = 0, target: int = 0) -> bool:
        """Set Query command parameters for inventory optimization."""
        if not self.is_connected:
            return False
        try:
            cmd = build_set_query_param_command(q_value, session, target)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            return response.success
        except Exception as e:
            logger.error(f"Failed to set query params: {e}")
            return False

    async def select_tag(self, epc_mask: str) -> bool:
        """Select specific tag for subsequent operations."""
        if not self.is_connected:
            return False
        try:
            cmd = build_select_tag_command(epc_mask)
            response_bytes = await asyncio.to_thread(self._send_command, cmd)
            response = M200ResponseParser.parse(response_bytes, strict_crc=False)
            return response.success
        except Exception as e:
            logger.error(f"Failed to select tag: {e}")
            return False


# Singleton instance
rfid_reader_service = RFIDReaderService()
