import json
import logging
from typing import Dict, Any, Union
from pywebpush import webpush, WebPushException
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class PushService:
    def __init__(self):
        pass

    def send_notification(self, subscription_info: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        Send a web push notification.
        Returns True if successful, False if subscription is invalid/expired (404/410).
        Raises WebPushException for other errors.
        """
        if not settings.VAPID_PRIVATE_KEY:
            logger.error("VAPID_PRIVATE_KEY is not set")
            raise ValueError("VAPID_PRIVATE_KEY is not set")

        try:
            # Ensure keys are strings
            if isinstance(subscription_info, str):
                subscription_info = json.loads(subscription_info)

            webpush(
                subscription_info=subscription_info,
                data=json.dumps(data),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_CLAIMS_SUB},
                ttl=60
            )
            return True
        except WebPushException as ex:
            if ex.response is not None and ex.response.status_code in [404, 410]:
                logger.warning(f"Subscription expired or invalid: {ex}")
                return False
            logger.error(f"Web Push error: {ex}")
            raise ex
        except Exception as e:
            logger.error(f"Unexpected error sending push: {e}")
            raise e

    async def send_to_user(self, user_id: str, title: str, body: str, data: Dict[str, Any] = None) -> int:
        """
        Send notification to all subscriptions for a specific user.
        Returns number of successful sends.
        """
        from prisma.models import PushSubscription
        from app.db.prisma import prisma_client

        if data is None:
            data = {}

        payload = {
            "title": title,
            "body": body,
            "icon": "/vite.svg", # Default icon
            "data": data
        }

        subscriptions = await PushSubscription.prisma().find_many(
            where={"userId": user_id}
        )

        sent_count = 0
        for sub in subscriptions:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }
            try:
                success = self.send_notification(sub_info, payload)
                if success:
                    sent_count += 1
                else:
                    # Invalid subscription, remove it
                    await PushSubscription.prisma().delete(where={"id": sub.id})
            except Exception as e:
                logger.error(f"Failed to send push to user {user_id} sub {sub.id}: {e}")
        
        return sent_count

push_service = PushService()
