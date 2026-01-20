"""
Theft detection service.
Monitors RFID scans and creates alerts for unpaid tags.
"""

import logging
from datetime import datetime
from typing import List, Optional

from app.db.prisma import prisma_client
from app.services.push_notifications import PushNotificationService

logger = logging.getLogger(__name__)


class TheftDetectionService:
    """
    Service for detecting unpaid tags and creating theft alerts.
    """

    def __init__(self):
        """Initialize theft detection service."""
        self.push_service = PushNotificationService()
        logger.info("Theft detection service initialized")

    async def check_tag_payment_status(self, epc: str, location: Optional[str] = None) -> bool:
        """
        Check if a scanned tag is paid. If not, create theft alert.

        Args:
            epc: Tag EPC code
            location: Where the tag was scanned

        Returns:
            True if tag is paid, False if unpaid (theft detected)
        """
        try:
            # Get tag mapping
            tag = await prisma_client.client.rfidtag.find_unique(
                where={"epc": epc}, include={"payment": True}
            )

            if not tag:
                logger.warning(f"Tag not found in database: {epc}")
                return True  # Unknown tag, don't alert

            # Check if tag is paid
            if tag.isPaid:
                logger.info(f"Tag {epc} is paid, no alert needed")
                return True

            # Tag is unpaid - create theft alert
            logger.warning(f"THEFT DETECTED: Unpaid tag scanned: {epc}")
            await self._create_theft_alert(tag, location)

            return False

        except Exception as e:
            logger.error(f"Error checking tag payment status: {str(e)}")
            return True  # Don't alert on errors

    async def _create_theft_alert(self, tag, location: Optional[str] = None):
        """
        Create a theft alert and notify stakeholders.

        Args:
            tag: RfidTag object
            location: Where the tag was detected
        """
        try:
            # Create theft alert
            alert = await prisma_client.client.theftalert.create(
                data={
                    "tagId": tag.id,
                    "epc": tag.epc,
                    "productDescription": tag.productDescription,
                    "location": location,
                    "detectedAt": datetime.now(),
                }
            )

            logger.info(f"Created theft alert: {alert.id} for tag {tag.epc}")

            # Get stakeholders to notify
            stakeholders = await self._get_stakeholders()

            # Send notifications
            await self._notify_stakeholders(alert, tag, stakeholders)

        except Exception as e:
            logger.error(f"Error creating theft alert: {str(e)}")

    async def _get_stakeholders(self) -> List:
        """
        Get users who should receive theft alerts.

        Returns:
            List of User objects
        """
        try:
            # Get users with SUPER_ADMIN, NETWORK_MANAGER, or STORE_MANAGER roles
            # who have opted in to receive theft alerts
            stakeholders = await prisma_client.client.user.find_many(
                where={
                    "AND": [
                        {
                            "role": {
                                "in": [
                                    "SUPER_ADMIN",
                                    "NETWORK_MANAGER",
                                    "STORE_MANAGER",
                                ]
                            }
                        },
                        {"receiveTheftAlerts": True},
                    ]
                }
            )

            logger.info(f"Found {len(stakeholders)} stakeholders to notify")
            return stakeholders

        except Exception as e:
            logger.error(f"Error getting stakeholders: {str(e)}")
            return []

    async def _notify_stakeholders(self, alert, tag, stakeholders: List):
        """
        Send push notifications to stakeholders.

        Args:
            alert: TheftAlert object
            tag: TagMapping object
            stakeholders: List of User objects
        """
        for user in stakeholders:
            try:
                # Create alert recipient record
                recipient = await prisma_client.client.alertrecipient.create(
                    data={"theftAlertId": alert.id, "userId": user.id}
                )

                # Send push notification
                message = self._create_alert_message(tag)
                success = await self.push_service.send_notification(
                    user_id=user.id,
                    title="🚨 התראת גניבה - Theft Alert",
                    body=message,
                    data={
                        "alert_id": alert.id,
                        "tag_epc": tag.epc,
                        "type": "theft_alert",
                    },
                )

                # Update delivery status
                if success:
                    await prisma_client.client.alertrecipient.update(
                        where={"id": recipient.id},
                        data={"delivered": True, "deliveredAt": datetime.now()},
                    )

                logger.info(f"Notified user {user.email} about theft alert {alert.id}")

            except Exception as e:
                logger.error(f"Error notifying user {user.id}: {str(e)}")

    def _create_alert_message(self, tag) -> str:
        """
        Create alert message text.

        Args:
            tag: TagMapping object

        Returns:
            Alert message string
        """
        product_desc = tag.productDescription or "לא ידוע"
        return f"זוהה תג לא משולם!\nתג: {tag.epc}\nמוצר: {product_desc}"

    async def resolve_alert(self, alert_id: str, resolved_by: str, notes: Optional[str] = None):
        """
        Mark a theft alert as resolved.

        Args:
            alert_id: Alert ID
            resolved_by: User ID who resolved
            notes: Resolution notes
        """
        try:
            await prisma_client.client.theftalert.update(
                where={"id": alert_id},
                data={
                    "resolved": True,
                    "resolvedAt": datetime.now(),
                    "resolvedBy": resolved_by,
                    "notes": notes,
                },
            )

            logger.info(f"Theft alert {alert_id} resolved by {resolved_by}")

        except Exception as e:
            logger.error(f"Error resolving alert: {str(e)}")
            raise
