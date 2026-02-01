from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from app.core.config import get_settings
from app.services.push_service import push_service

from prisma.models import PushSubscription

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

class SubscriptionSchema(BaseModel):
    endpoint: str
    keys: Dict[str, str]
    userId: Optional[str] = None

class NotificationSchema(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    userId: Optional[str] = None # Target specific user

@router.get("/vapid-public-key")
async def get_vapid_public_key():
    if not settings.VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="VAPID_PUBLIC_KEY not configured")
    return {"publicKey": settings.VAPID_PUBLIC_KEY}

@router.post("/subscribe", status_code=201)
async def subscribe(subscription: SubscriptionSchema):
    try:
        # Check if subscription already exists
        existing = await PushSubscription.prisma().find_unique(
            where={"endpoint": subscription.endpoint}
        )
        
        if existing:
            # Update user if changed
            if subscription.userId and existing.userId != subscription.userId:
                logger.info(f"Updating subscription {existing.id} user: {existing.userId} -> {subscription.userId}")
                await PushSubscription.prisma().update(
                    where={"id": existing.id},
                    data={"userId": subscription.userId}
                )
            return {"message": "Subscription updated"}

        # Create new subscription
        # Create new subscription
        logger.info(f"Creating new subscription for endpoint: {subscription.endpoint[:20]}...")
        new_sub = await PushSubscription.prisma().create(
            data={
                "endpoint": subscription.endpoint,
                "p256dh": subscription.keys.get("p256dh"),
                "auth": subscription.keys.get("auth"),
                "userId": subscription.userId
            }
        )
        logger.info(f"Subscription created: {new_sub.id}")
        return {"message": "Subscribed successfully"}
    except Exception as e:
        logger.error(f"Error subscribing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-notification")
async def send_notification(notification: NotificationSchema):
    """
    Send notification to users. 
    If userId is provided, sends to that user's subscriptions.
    Otherwise, sends to ALL subscriptions (broadcast).
    """
    payload = {
        "title": notification.title,
        "body": notification.body,
        "icon": notification.icon or "/icon.png",
        "data": notification.data or {}
    }

    subscriptions = []
    if notification.userId:
        subscriptions = await PushSubscription.prisma().find_many(
            where={"userId": notification.userId}
        )
    else:
        # Broadcast - limit to 100 for safety in this MVP
        subscriptions = await PushSubscription.prisma().find_many(take=100)

    if not subscriptions:
        return {"message": "No subscriptions found", "count": 0}

    sent_count = 0
    failed_count = 0
    removed_count = 0

    for sub in subscriptions:
        sub_info = {
            "endpoint": sub.endpoint,
            "keys": {
                "p256dh": sub.p256dh,
                "auth": sub.auth
            }
        }
        try:
            success = push_service.send_notification(sub_info, payload)
            if success:
                sent_count += 1
            else:
                # Subscription invalid/gone, remove it
                await PushSubscription.prisma().delete(where={"id": sub.id})
                removed_count += 1
                failed_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send to {sub.id}: {e}")

    return {
        "message": "Notification process completed",
        "sent": sent_count,
        "failed": failed_count,
        "removed": removed_count
    }
