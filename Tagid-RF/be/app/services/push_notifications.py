"""
Push notification service using Firebase Cloud Messaging (FCM).
Sends push notifications to mobile app users.
"""

import logging
from typing import Any, Dict, Optional

import firebase_admin
from app.core.config import settings
from firebase_admin import credentials

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Service for sending push notifications via Firebase Cloud Messaging.
    """

    def __init__(self):
        """Initialize Firebase Admin SDK."""
        try:
            # Initialize Firebase if not already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(
                    {
                        "type": "service_account",
                        "project_id": settings.FCM_PROJECT_ID,
                        "private_key": settings.FCM_SERVER_KEY,
                        # Add other required fields from your Firebase service account
                    }
                )
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {str(e)}")

    async def send_notification(
        self, user_id: str, title: str, body: str, data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a push notification to a user.

        Args:
            user_id: User ID to send notification to
            title: Notification title
            body: Notification body
            data: Additional data payload

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # In a real implementation, you would:
            # 1. Get user's FCM token from database
            # 2. Send notification using FCM

            # For now, we'll log the notification
            logger.info(
                f"Sending push notification to user {user_id}: "
                f"Title: {title}, Body: {body}"
            )

            # Example FCM message (uncomment when you have FCM tokens)
            # message = messaging.Message(
            #     notification=messaging.Notification(
            #         title=title,
            #         body=body
            #     ),
            #     data=data or {},
            #     token=user_fcm_token  # Get from database
            # )
            #
            # response = messaging.send(message)
            # logger.info(f"Successfully sent message: {response}")

            return True

        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False

    async def send_bulk_notifications(
        self,
        user_ids: list,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, bool]:
        """
        Send push notifications to multiple users.

        Args:
            user_ids: List of user IDs
            title: Notification title
            body: Notification body
            data: Additional data payload

        Returns:
            Dict mapping user_id to success status
        """
        results = {}

        for user_id in user_ids:
            success = await self.send_notification(user_id, title, body, data)
            results[user_id] = success

        return results
