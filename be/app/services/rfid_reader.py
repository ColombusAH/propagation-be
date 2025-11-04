"""
RFID Reader Service for Chafon CF-H906 UHF Handheld Reader.

This service handles connection to the RFID reader and tag scanning operations.
Supports multiple connection methods:
1. chafon-rfid Python library (if available)
2. Direct TCP/IP socket connection via WiFi
3. Android app bridge (via HTTP API)

For MVP, this is a skeleton implementation with TODO markers for
actual hardware integration.
"""
import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timezone
from app.core.config import get_settings
from app.services.database import SessionLocal
from app.models.rfid_tag import RFIDTag, RFIDScanHistory
from app.routers.websocket import manager

logger = logging.getLogger(__name__)
settings = get_settings()


class RFIDReaderService:
    """Service for managing RFID reader connection and operations."""
    
    def __init__(self):
        self.reader_ip = getattr(settings, 'RFID_READER_IP', '192.168.1.100')
        self.reader_port = getattr(settings, 'RFID_READER_PORT', 4001)
        self.connection_type = getattr(settings, 'RFID_CONNECTION_TYPE', 'wifi')
        self.reader_id = getattr(settings, 'RFID_READER_ID', 'CF-H906-001')
        self.is_connected = False
        self.is_scanning = False
        self.reader = None  # Will hold reader connection object
        self.reader_socket = None  # For TCP/IP connection
        self.writer = None  # For TCP/IP connection
        
    async def connect(self) -> bool:
        """
        Connect to CF-H906 via configured method (WiFi/Bluetooth/Serial).
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.connection_type == 'wifi':
                return await self._connect_wifi()
            elif self.connection_type == 'bluetooth':
                return await self._connect_bluetooth()
            elif self.connection_type == 'serial':
                return await self._connect_serial()
            else:
                logger.error(f"Unknown connection type: {self.connection_type}")
                return False
        except Exception as e:
            logger.error(f"Connection failed: {e}", exc_info=True)
            return False
    
    async def _connect_wifi(self) -> bool:
        """Connect via TCP/IP WiFi."""
        try:
            # TODO: Implement actual TCP/IP connection to CF-H906
            # Option 1: Use chafon-rfid library if available
            # try:
            #     from chafon_rfid import Reader
            #     self.reader = Reader(self.reader_ip, self.reader_port)
            #     await self.reader.connect()
            #     self.is_connected = True
            #     logger.info(f"Connected to CF-H906 via WiFi at {self.reader_ip}:{self.reader_port}")
            #     return True
            # except ImportError:
            #     logger.warning("chafon-rfid library not available, using direct socket")
            
            # Option 2: Direct TCP/IP socket connection
            self.reader_socket, self.writer = await asyncio.open_connection(
                self.reader_ip, self.reader_port
            )
            self.is_connected = True
            logger.info(f"Connected to CF-H906 via WiFi at {self.reader_ip}:{self.reader_port}")
            return True
        except Exception as e:
            logger.error(f"WiFi connection failed: {e}")
            self.is_connected = False
            return False
    
    async def _connect_bluetooth(self) -> bool:
        """Connect via Bluetooth."""
        # TODO: Implement Bluetooth connection
        logger.warning("Bluetooth connection not yet implemented")
        return False
    
    async def _connect_serial(self) -> bool:
        """Connect via Serial/USB."""
        # TODO: Implement serial connection
        logger.warning("Serial connection not yet implemented")
        return False
    
    async def disconnect(self):
        """Disconnect from RFID reader."""
        try:
            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()
            if hasattr(self, 'reader') and self.reader:
                # Close reader connection if using library
                if hasattr(self.reader, 'disconnect'):
                    await self.reader.disconnect()
            
            self.is_connected = False
            self.is_scanning = False
            logger.info("Disconnected from RFID reader")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def start_scanning(self, callback: Optional[Callable] = None):
        """
        Start continuous tag inventory scanning.
        
        For each tag scanned:
        - Parse tag data (EPC, TID, RSSI, etc.)
        - Save to database (upsert tags, insert history)
        - Broadcast via WebSocket
        - Call callback if provided
        
        Args:
            callback: Optional callback function to call for each tag
        """
        if not self.is_connected:
            logger.error("Cannot start scanning: not connected to reader")
            return
        
        if self.is_scanning:
            logger.warning("Scanning already in progress")
            return
        
        self.is_scanning = True
        logger.info("Starting continuous tag scanning...")
        
        # Start scanning in background task
        asyncio.create_task(self._scan_loop(callback))
    
    async def _scan_loop(self, callback: Optional[Callable] = None):
        """Main scanning loop."""
        while self.is_scanning and self.is_connected:
            try:
                # Read tags from reader
                tags = await self.read_single_tag()
                
                if tags:
                    # Process each tag
                    for tag_data in tags if isinstance(tags, list) else [tags]:
                        await self._process_tag(tag_data, callback)
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in scan loop: {e}", exc_info=True)
                await asyncio.sleep(1)  # Wait before retrying
    
    async def _process_tag(self, tag_data: Dict[str, Any], callback: Optional[Callable] = None):
        """
        Process a scanned tag: save to DB and broadcast via WebSocket.
        
        Args:
            tag_data: Parsed tag data dictionary
            callback: Optional callback function
        """
        try:
            db = SessionLocal()
            try:
                # Check if tag exists
                existing_tag = db.query(RFIDTag).filter(RFIDTag.epc == tag_data['epc']).first()
                
                if existing_tag:
                    # Update existing tag
                    existing_tag.read_count += 1
                    existing_tag.last_seen = datetime.now(timezone.utc)
                    if tag_data.get('rssi'):
                        existing_tag.rssi = tag_data['rssi']
                    if tag_data.get('antenna_port'):
                        existing_tag.antenna_port = tag_data['antenna_port']
                    if tag_data.get('frequency'):
                        existing_tag.frequency = tag_data['frequency']
                    if tag_data.get('location'):
                        existing_tag.location = tag_data['location']
                    if tag_data.get('tid'):
                        existing_tag.tid = tag_data['tid']
                    db.commit()
                    db.refresh(existing_tag)
                    tag_id = existing_tag.id
                else:
                    # Create new tag
                    new_tag = RFIDTag(
                        epc=tag_data['epc'],
                        tid=tag_data.get('tid'),
                        rssi=tag_data.get('rssi'),
                        antenna_port=tag_data.get('antenna_port'),
                        frequency=tag_data.get('frequency'),
                        pc=tag_data.get('pc'),
                        crc=tag_data.get('crc'),
                        location=tag_data.get('location'),
                        metadata=tag_data.get('metadata'),
                    )
                    db.add(new_tag)
                    db.commit()
                    db.refresh(new_tag)
                    tag_id = new_tag.id
                
                # Always create history entry
                history = RFIDScanHistory(
                    epc=tag_data['epc'],
                    tid=tag_data.get('tid'),
                    rssi=tag_data.get('rssi'),
                    antenna_port=tag_data.get('antenna_port'),
                    frequency=tag_data.get('frequency'),
                    location=tag_data.get('location'),
                    reader_id=self.reader_id,
                    metadata=tag_data.get('metadata'),
                    scanned_at=datetime.now(timezone.utc),
                )
                db.add(history)
                db.commit()
                
                # Broadcast via WebSocket
                await manager.broadcast({
                    "type": "tag_scanned",
                    "data": {
                        "tag_id": tag_id,
                        "epc": tag_data['epc'],
                        "tid": tag_data.get('tid'),
                        "rssi": tag_data.get('rssi'),
                        "antenna_port": tag_data.get('antenna_port'),
                        "frequency": tag_data.get('frequency'),
                        "location": tag_data.get('location'),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                })
                
                # Call callback if provided
                if callback:
                    await callback(tag_data) if asyncio.iscoroutinefunction(callback) else callback(tag_data)
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing tag: {e}", exc_info=True)
    
    async def stop_scanning(self):
        """Stop continuous scanning."""
        self.is_scanning = False
        logger.info("Stopped tag scanning")
    
    async def read_single_tag(self) -> Optional[Dict[str, Any]]:
        """
        Read a single tag and return data.
        
        Returns:
            dict: Tag data or None if no tag found
        """
        if not self.is_connected:
            logger.error("Cannot read tag: not connected")
            return None
        
        try:
            # TODO: Implement actual tag reading from CF-H906
            # Option 1: Using chafon-rfid library
            # if hasattr(self, 'reader') and self.reader:
            #     tags = await self.reader.inventory()
            #     if tags:
            #         return self._parse_tag(tags[0])
            
            # Option 2: Direct TCP/IP command
            # command = self._build_inventory_command()
            # response = await self.send_command(command)
            # return self._parse_response(response)
            
            # For MVP: Return mock data for testing
            # Remove this when implementing real reader
            logger.debug("read_single_tag called - implement actual reader command")
            return None
            
        except Exception as e:
            logger.error(f"Error reading tag: {e}")
            return None
    
    async def write_tag(self, epc: str, data: Dict[str, Any]) -> bool:
        """
        Write data to RFID tag (EPC, user memory).
        
        Args:
            epc: Target EPC to write
            data: Data to write (epc, user_memory, etc.)
        
        Returns:
            bool: True if write successful
        """
        if not self.is_connected:
            logger.error("Cannot write tag: not connected")
            return False
        
        try:
            # TODO: Implement actual tag writing
            # command = self._build_write_command(epc, data)
            # response = await self.send_command(command)
            # return self._parse_write_response(response)
            
            logger.warning("Tag writing not yet implemented")
            return False
            
        except Exception as e:
            logger.error(f"Error writing tag: {e}")
            return False
    
    async def send_command(self, command: bytes) -> bytes:
        """
        Send command to reader and receive response.
        
        Args:
            command: Command bytes to send
        
        Returns:
            bytes: Response from reader
        """
        if not self.is_connected or not self.writer:
            raise ConnectionError("Not connected to reader")
        
        self.writer.write(command)
        await self.writer.drain()
        response = await self.reader_socket.read(1024)
        return response
    
    async def get_reader_info(self) -> Dict[str, Any]:
        """
        Get reader information (model, firmware, serial number, etc.).
        
        Returns:
            dict: Reader information
        """
        if not self.is_connected:
            return {"connected": False}
        
        try:
            # TODO: Implement actual reader info query
            # command = self._build_info_command()
            # response = await self.send_command(command)
            # return self._parse_info_response(response)
            
            return {
                "connected": True,
                "model": "CF-H906",
                "ip": self.reader_ip,
                "port": self.reader_port,
                "reader_id": self.reader_id,
                "connection_type": self.connection_type,
            }
            
        except Exception as e:
            logger.error(f"Error getting reader info: {e}")
            return {"connected": False, "error": str(e)}
    
    def _parse_tag(self, raw_data: Any) -> Dict[str, Any]:
        """
        Parse raw tag data from reader into standardized format.
        
        Args:
            raw_data: Raw tag data from reader
        
        Returns:
            dict: Parsed tag data
        """
        # TODO: Implement parsing based on actual reader output format
        # This is a placeholder structure
        return {
            "epc": "",  # Extract from raw_data
            "tid": None,  # Extract if available
            "rssi": None,  # Extract signal strength
            "antenna_port": None,  # Extract antenna number
            "frequency": None,  # Extract frequency
            "pc": None,  # Extract protocol control
            "crc": None,  # Extract CRC
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global instance
rfid_reader_service = RFIDReaderService()

