"""API endpoints for user notification settings."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies.auth import get_current_user
from app.db.dependencies import get_db
from prisma import Prisma

router = APIRouter()


class NotificationSetting(BaseModel):
    """Single notification channel setting."""

    channel: str  # PUSH, SMS, EMAIL
    enabled: bool


class NotificationSettingsResponse(BaseModel):
    """Response for notification settings."""

    push: bool = True
    sms: bool = False
    email: bool = True
    darkMode: bool = False


class NotificationSettingsUpdate(BaseModel):
    """Request to update notification settings."""

    push: bool | None = None
    sms: bool | None = None
    email: bool | None = None
    darkMode: bool | None = None


@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    db: Prisma = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> NotificationSettingsResponse:
    """
    Get notification settings for the current user.
    """
    print(f"DEBUG: get_notification_settings called for user {current_user.id}")
    try:
        # Check if NotificationPreference records exist for user
        preferences = await db.notificationpreference.find_many(where={"userId": current_user.id})

        # Default values
        settings = {
            "push": True,
            "sms": False,
            "email": True,
        }

        # Update from database if found
        for pref in preferences:
            channel = pref.channelType.lower()
            if channel in settings:
                settings[channel] = pref.enabled

        # Add darkMode from User model
        settings["darkMode"] = getattr(current_user, "darkMode", False)

        return NotificationSettingsResponse(**settings)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings: NotificationSettingsUpdate,
    db: Prisma = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> NotificationSettingsResponse:
    """
    Update notification settings for the current user.
    """
    print(
        f"DEBUG: update_notification_settings called for user {current_user.id} with data {settings}"
    )
    try:
        # Map of channel name to update value
        updates = {
            "PUSH": settings.push,
            "SMS": settings.sms,
            "EMAIL": settings.email,
        }

        # Update darkMode if provided
        if settings.darkMode is not None:
            try:
                await db.user.update(
                    where={"id": current_user.id}, data={"darkMode": settings.darkMode}
                )
            except Exception as e:
                # Log error but don't fail the whole request
                # This happens if migration hasn't run yet
                print(f"Warning: Could not update darkMode: {e}")

        for channel, enabled in updates.items():
            if enabled is not None:
                # Search for existing preference first to handle NULL in unique key safely
                existing = await db.notificationpreference.find_first(
                    where={
                        "userId": current_user.id,
                        "channelType": channel,
                        "notificationType": None,
                    }
                )

                if existing:
                    await db.notificationpreference.update(
                        where={"id": existing.id}, data={"enabled": enabled}
                    )
                else:
                    await db.notificationpreference.create(
                        data={
                            "userId": current_user.id,
                            "channelType": channel,
                            "enabled": enabled,
                            "notificationType": None,
                        }
                    )

        # Fetch fresh user data to include updated darkMode
        fresh_user = await db.user.find_unique(where={"id": current_user.id})

        # Return updated settings
        return await get_notification_settings(db, fresh_user or current_user)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-push")
async def test_push_notification(
    db: Prisma = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """
    Send a test push notification to the current user.
    """
    from app.services.push_notification_service import PushNotificationService
    
    service = PushNotificationService(db)
    
    # Trigger a simulated theft alert for this user
    # Note: we pass actual user data to make it real
    result = await service.send_theft_alert(
        tag_id="test-tag-123",
        epc="E1234567890ABCDEF",
        location="Testing Zone",
    )
    
    return {
        "message": "Test push notification triggered",
        "result": result
    }
