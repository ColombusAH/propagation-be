"""
Push Notification Service

Provides functionality for:
- Sending theft alerts when unpaid items exit through gate
- Notifying users who have opted in for alerts
- Logging all alerts to database
"""

import logging
from datetime import datetime
from typing import Optional

from prisma import Prisma

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications and alerts"""

    def __init__(self, db: Prisma):
        self.db = db

    async def send_theft_alert(
        self,
        tag_id: str,
        epc: str,
        reader_id: Optional[str] = None,
        location: Optional[str] = None,
    ) -> dict:
        """
        Send theft alert when an unpaid item passes through gate.

        Flow:
        1. Get tag and product info
        2. Create TheftAlert record
        3. Find all users with receiveTheftAlerts=True
        4. Send notification to each user
        5. Log delivery status
        """
        logger.warning(f"🚨 THEFT ALERT: Tag {epc} detected at gate!")

        # Get tag info
        tag = await self.db.rfidtag.find_unique(where={"id": tag_id})
        if not tag:
            tag = await self.db.rfidtag.find_unique(where={"epc": epc})

        product_description = "Unknown Product"
        if tag:
            product_description = tag.productDescription or f"EPC: {tag.epc}"

        # Create TheftAlert record
        alert = await self.db.theftalert.create(
            data={
                "tagId": tag.id if tag else tag_id,
                "epc": epc,
                "productDescription": product_description,
                "detectedAt": datetime.now(),
                "location": location or "Main Gate",
                "resolved": False,
            }
        )

        logger.info(f"Created TheftAlert: {alert.id}")

        # Find users who want to receive alerts
        alert_users = await self.db.user.find_many(where={"receiveTheftAlerts": True})

        logger.info(f"Found {len(alert_users)} users to notify")

        recipients_notified = 0

        for user in alert_users:
            try:
                # Create AlertRecipient record
                await self.db.alertrecipient.create(
                    data={
                        "theftAlertId": alert.id,
                        "userId": user.id,
                        "sentAt": datetime.now(),
                        "delivered": True,  # In POC, assume delivery
                        "deliveredAt": datetime.now(),
                    }
                )

                # In production, this would send actual push notification
                # For POC, we just log it
                logger.info(f"📱 Push sent to {user.email}: {product_description}")
                recipients_notified += 1

            except Exception as e:
                logger.error(f"Failed to notify {user.email}: {e}")

        return {
            "alert_id": alert.id,
            "tag_epc": epc,
            "product": product_description,
            "recipients_notified": recipients_notified,
            "timestamp": datetime.now().isoformat(),
        }

    async def check_gate_scan(self, epc: str, reader_id: str) -> dict:
        """
        Check if a tag passing through gate is paid.
        If not paid, trigger theft alert.

        Returns:
            dict with status and alert info if triggered
        """
        # Verify this is a gate reader
        reader = await self.db.rfidreader.find_unique(where={"id": reader_id})

        if not reader or reader.type != "GATE":
            logger.debug(f"Reader {reader_id} is not a gate, skipping check")
            return {"status": "skipped", "reason": "not_gate_reader"}

        # Find the tag
        tag = await self.db.rfidtag.find_unique(where={"epc": epc})

        if not tag:
            logger.warning(f"Unknown tag {epc} at gate - creating alert")
            # Unknown tag is also suspicious
            alert_result = await self.send_theft_alert(
                tag_id="unknown", epc=epc, reader_id=reader_id, location=reader.location
            )
            return {"status": "alert", "alert": alert_result}

        # Check if paid
        if tag.isPaid:
            logger.info(f"Tag {epc} is paid - OK to exit")

            # Update status to EXITED
            await self.db.rfidtag.update(
                where={"id": tag.id}, data={"status": "SOLD"}  # Keep as SOLD after exit
            )

            return {"status": "ok", "message": "Paid item exiting"}

        # NOT PAID - TRIGGER ALERT!
        logger.warning(f"🚨 UNPAID TAG {epc} AT GATE!")

        alert_result = await self.send_theft_alert(
            tag_id=tag.id, epc=epc, reader_id=reader_id, location=reader.location
        )

        # Update tag status
        await self.db.rfidtag.update(where={"id": tag.id}, data={"status": "STOLEN"})

        return {"status": "alert", "alert": alert_result}


async def create_notification_service(db: Prisma) -> PushNotificationService:
    """Factory function to create notification service"""
    return PushNotificationService(db)
