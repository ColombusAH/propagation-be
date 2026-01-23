"""
Tag Listener Service - FastAPI Integration

This service provides real-time RFID tag data from the M-200 reader
to the FastAPI application and admin dashboard.

The service runs the TCP listener as a background thread and provides:
- Real-time tag events via callback
- Recent tag history for API access
- Statistics for admin dashboard
"""

import asyncio
import logging
import threading
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from app.routers.websocket import manager

logger = logging.getLogger(__name__)

# Import from standalone listener (if run as module)
# Import from standalone listener (if run as module)
try:
    from tag_listener_server import (set_tag_callback, start_inventory,
                                     start_server, stop_inventory, tag_store)
except ImportError:
    # Fallback - define minimal storage here
    def set_tag_callback(cb):
        pass

    def start_inventory():
        return False

    def stop_inventory():
        return False

    # ... (TagStore implementation remains if needed, but imports are key)
    # ... (TagStore implementation remains if needed, but imports are key)
    from app.services.tag_store import TagStore

    tag_store = TagStore()


class TagListenerService:
    """
    Service for managing the RFID tag listener and providing data to FastAPI.
    """

    def __init__(self, port: int = 4001):
        self.port = port
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        self._loop = None

    def start_scan(self) -> bool:
        """Send Start Inventory command to connected reader."""
        logger.info("Sending Start Inventory command (Answer Mode)...")
        return start_inventory()

    def stop_scan(self) -> bool:
        """Send Stop Inventory command to connected reader."""
        logger.info("Sending Stop Inventory command...")
        return stop_inventory()

    def start(self):
        """Start the tag listener in a background thread."""
        if self._running:
            logger.warning("Tag listener already running")
            return

        # Capture current event loop for thread-safe scheduling
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.warning("No running event loop captured for TagListenerService")

        # Register callback with the low-level server
        set_tag_callback(self.on_tag_scanned_sync)

        self._running = True
        self._thread = threading.Thread(
            target=self._run_listener, daemon=True, name="TagListenerThread"
        )
        self._thread.start()
        logger.info(f"Tag listener started on port {self.port}")

    def stop(self):
        """Stop the tag listener."""
        self._running = False
        logger.info("Tag listener stopped")

    def _run_listener(self):
        """Run the listener (in background thread)."""
        try:
            start_server(self.port)
        except Exception as e:
            logger.error(f"Tag listener error: {e}")

    def add_tag_callback(self, callback: Callable):
        """Add a callback to be called when a tag is scanned."""
        self._callbacks.append(callback)

    def on_tag_scanned_sync(self, tag_data: Dict[str, Any]):
        """Called from background thread when tag is scanned."""
        # Broadcast to WebSocket via main loop
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast_tag(tag_data), self._loop)

        # Invoke synchronous callbacks immediately
        for callback in self._callbacks:
            try:
                callback(tag_data)
            except Exception as e:
                logger.error(f"Tag callback error: {e}")

    async def _broadcast_tag(self, tag_data: Dict[str, Any]):
        """Broadcast tag data to WebSocket clients and check for theft."""
        try:
            from app.db.prisma import prisma_client
            from app.services.tag_encryption import get_encryption_service
            from app.services.theft_detection import TheftDetectionService

            theft_service = TheftDetectionService()
            epc = tag_data.get("epc")
            tag_id = tag_data.get("tag_id")
            reader_ip = tag_data.get("reader_ip", "Unknown")

            existing_tag_db = None
            reader_db = None
            encryption_status = {"is_encrypted": False, "decrypted_qr": None}

            async with prisma_client.client as db:
                # 1. Fetch Reader Info
                if reader_ip != "Unknown":
                    reader_db = await db.rfidreader.find_unique(
                        where={"ipAddress": reader_ip}
                    )

                # 2. Fetch Tag Info
                if epc:
                    try:
                        # Fetch tag with relations
                        rfid_tag = await db.rfidtag.find_unique(
                            where={"epc": epc}, include={"payment": True}
                        )

                        if rfid_tag:
                            existing_tag_db = rfid_tag

                            # Handle QR Decryption...
                            if rfid_tag.encryptedQr:
                                # (Encryption logic remains)
                                encryption_status["is_encrypted"] = True
                                try:
                                    encrypt_svc = get_encryption_service()
                                    encryption_status["decrypted_qr"] = (
                                        encrypt_svc.decrypt_qr(rfid_tag.encryptedQr)
                                    )
                                except Exception as e:
                                    logger.error(
                                        f"Error decrypting QR code for EPC {epc}: {e}"
                                    )
                                    encryption_status["decrypted_qr"] = (
                                        "Decryption Failed"
                                    )

                    except Exception as e:
                        logger.error(f"Prisma check error: {e}")

            # Broadcast to WebSocket
            tag_payload = {
                "tag_id": tag_id,
                "epc": epc,
                "rssi": tag_data.get("rssi"),
                "antenna_port": tag_data.get("antenna_port"),
                "timestamp": tag_data.get("timestamp"),
                "reader_ip": reader_ip,
                # Product Info from Prisma
                "product_name": (
                    existing_tag_db.productDescription if existing_tag_db else None
                ),
                "product_sku": existing_tag_db.productId if existing_tag_db else None,
                "price": 0,  # TODO: Link to Product model for actual price
                "is_paid": existing_tag_db.isPaid if existing_tag_db else False,
                **encryption_status,
            }

            await manager.broadcast(
                {
                    "type": "tag_scanned",
                    "data": tag_payload,
                }
            )

            # THEFT ALERT LOGIC
            # Use the dedicated service for comprehensive theft detection and notification
            if epc and reader_db and reader_db.type == "GATE":
                # Only check for theft at exit gates
                is_paid = await theft_service.check_tag_payment_status(
                    epc, location=f"{reader_db.name} ({reader_ip})"
                )

                if not is_paid:
                    # Additional real-time notification via WebSocket (Service handles DB/SMS/Push)
                    await manager.broadcast(
                        {
                            "type": "theft_alert",
                            "data": {
                                "message": f"Unpaid item detected at {reader_db.name}: {existing_tag_db.productDescription if existing_tag_db else epc}",
                                "tag": tag_payload,
                                "severity": "critical",
                                "timestamp": datetime.now().isoformat(),
                                "location": reader_db.location or reader_db.name,
                            },
                        }
                    )
            elif epc and reader_db and reader_db.type == "FIXED":
                # Logic for shelf movement or inventory updates can go here
                pass

        except Exception as e:
            logger.error(f"Error broadcasting tag: {e}", exc_info=True)

    def get_recent_tags(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent scanned tags."""
        return tag_store.get_recent(count)

    def get_stats(self) -> Dict[str, Any]:
        """Get listener statistics."""
        return {
            "running": self._running,
            "port": self.port,
            "total_scans": tag_store.get_total_count(),
            "unique_epcs": tag_store.get_unique_count(),
        }


# Singleton instance
tag_listener_service = TagListenerService()
