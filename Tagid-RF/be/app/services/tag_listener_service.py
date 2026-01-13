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
    from tag_listener_server import (
        set_tag_callback,
        start_inventory,
        start_server,
        stop_inventory,
        tag_store,
    )
except ImportError:
    # Fallback - define minimal storage here
    def set_tag_callback(cb):
        pass

    def start_inventory():
        return False

    def stop_inventory():
        return False

    # ... (TagStore implementation remains if needed, but imports are key)
    class TagStore:
        def __init__(self):
            self._tags = []
            self._unique = set()
            self._lock = threading.Lock()

        def add_tag(self, tag_data):
            with self._lock:
                is_new = tag_data.get("epc") not in self._unique
                self._unique.add(tag_data.get("epc"))
                self._tags.append(tag_data)
                return is_new

        def get_recent(self, count=50):
            with self._lock:
                return list(reversed(self._tags[-count:]))

        def get_unique_count(self):
            with self._lock:
                return len(self._unique)

        def get_total_count(self):
            with self._lock:
                return len(self._tags)

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
        """Broadcast tag data to WebSocket clients."""
        try:
            from app.db.prisma import prisma_client
            from app.models.rfid_tag import RFIDTag
            from app.services.database import SessionLocal
            from app.services.encryption import decrypt_qr_code

            epc = tag_data.get("epc")
            tag_id = tag_data.get("tag_id")

            existing_tag_db = None
            encryption_status = {"is_encrypted": False, "decrypted_qr": None}

            if epc:
                # 1. Check Prisma for Encryption Mapping (Anti-Counterfeit)
                try:
                    async with prisma_client.client as db:
                        mapping = await db.tagmapping.find_unique(where={"epc": epc})
                        if mapping and mapping.encryptedQr:
                            encryption_status["is_encrypted"] = True
                            try:
                                encryption_status["decrypted_qr"] = decrypt_qr_code(
                                    mapping.encryptedQr
                                )
                            except Exception as e:
                                logger.error(f"Error decrypting QR code for EPC {epc}: {e}")
                                encryption_status["decrypted_qr"] = "Decryption Failed"
                except Exception as e:
                    logger.error(f"Prisma check error: {e}")

                # 2. Check SQLAlchemy for Product/Payment Info (Inventory/Theft)
                try:

                    def get_tag_info():
                        db = SessionLocal()
                        try:
                            return db.query(RFIDTag).filter(RFIDTag.epc == epc).first()
                        finally:
                            db.close()

                    existing_tag_db = await asyncio.to_thread(get_tag_info)
                except Exception as e:
                    logger.error(f"SQLAlchemy check error: {e}")

            # Broadcast to WebSocket
            tag_payload = {
                "tag_id": tag_id,
                "epc": epc,
                "rssi": tag_data.get("rssi"),
                "antenna_port": tag_data.get("antenna_port"),
                "timestamp": tag_data.get("timestamp"),
                # Product Info from SQLAlchemy
                "product_name": existing_tag_db.product_name if existing_tag_db else None,
                "product_sku": existing_tag_db.product_sku if existing_tag_db else None,
                "price": existing_tag_db.price_cents if existing_tag_db else None,
                "is_paid": existing_tag_db.is_paid if existing_tag_db else False,
                **encryption_status,
            }

            await manager.broadcast(
                {
                    "type": "tag_scanned",
                    "data": tag_payload,
                }
            )

            # THEFT ALERT LOGIC
            # If tag exists, has a product mapped, and is NOT paid
            if existing_tag_db and existing_tag_db.product_name and not existing_tag_db.is_paid:
                logger.warning(
                    f"🚨 THEFT ALERT: Unpaid item scanned! EPC: {epc}, Product: {existing_tag_db.product_name}"
                )
                await manager.broadcast(
                    {
                        "type": "theft_alert",
                        "data": {
                            "message": f"Unpaid item detected: {existing_tag_db.product_name}",
                            "tag": tag_payload,
                            "severity": "critical",
                            "timestamp": datetime.now().isoformat(),
                            "location": "Gate",  # Assuming getting scanned here means passing the gate
                        },
                    }
                )

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
