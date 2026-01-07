"""
Notification management API endpoints.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.store import Notification, NotificationPreference, User
from app.services.database import get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ============= Pydantic Schemas =============

class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preferences."""
    notification_type: str
    channel_push: bool = True
    channel_sms: bool = False
    channel_email: bool = False
    store_filter_id: Optional[int] = None


class NotificationPreferenceResponse(BaseModel):
    """Schema for notification preference response."""
    id: int
    notification_type: str
    channel_push: bool
    channel_sms: bool
    channel_email: bool
    store_filter_id: Optional[int]

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: int
    notification_type: str
    title: str
    message: str
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True


class SendNotificationRequest(BaseModel):
    """Schema for sending a notification."""
    user_id: int
    notification_type: str
    title: str
    message: str
    store_id: Optional[int] = None
    tag_epc: Optional[str] = None


# ============= Notification Types =============

NOTIFICATION_TYPES = [
    "UNPAID_EXIT",      # Security: unpaid tag at exit
    "SALE",             # New sale completed
    "LOW_STOCK",        # Low inventory warning
    "GOAL_ACHIEVED",    # Sales goal reached
    "SYSTEM_UPDATE",    # System update available
    "NEW_USER",         # New user joined
    "ERROR",            # System error
]


# ============= API Endpoints =============

@router.get("/preferences", response_model=List[NotificationPreferenceResponse])
async def get_preferences(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get notification preferences for a user.
    
    Returns default preferences if user has no custom settings.
    """
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == user_id
    ).all()
    
    # If no preferences exist, return defaults
    if not prefs:
        defaults = []
        for ntype in NOTIFICATION_TYPES:
            # Security alerts default to all channels
            is_security = ntype == "UNPAID_EXIT"
            defaults.append(NotificationPreferenceResponse(
                id=0,
                notification_type=ntype,
                channel_push=True,
                channel_sms=is_security,
                channel_email=is_security,
                store_filter_id=None
            ))
        return defaults
    
    return [NotificationPreferenceResponse(
        id=p.id,
        notification_type=p.notification_type,
        channel_push=p.channel_push,
        channel_sms=p.channel_sms,
        channel_email=p.channel_email,
        store_filter_id=p.store_filter_id
    ) for p in prefs]


@router.put("/preferences", response_model=List[NotificationPreferenceResponse])
async def update_preferences(
    user_id: int,
    preferences: List[NotificationPreferenceUpdate],
    db: Session = Depends(get_db)
):
    """
    Update notification preferences for a user.
    
    Creates or updates preferences for each notification type.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = []
    for pref_data in preferences:
        # Validate notification type
        if pref_data.notification_type not in NOTIFICATION_TYPES:
            continue
        
        # Find or create preference
        pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type == pref_data.notification_type
        ).first()
        
        if pref:
            # Update existing
            pref.channel_push = pref_data.channel_push
            pref.channel_sms = pref_data.channel_sms
            pref.channel_email = pref_data.channel_email
            pref.store_filter_id = pref_data.store_filter_id
        else:
            # Create new
            pref = NotificationPreference(
                user_id=user_id,
                notification_type=pref_data.notification_type,
                channel_push=pref_data.channel_push,
                channel_sms=pref_data.channel_sms,
                channel_email=pref_data.channel_email,
                store_filter_id=pref_data.store_filter_id
            )
            db.add(pref)
        
        db.commit()
        db.refresh(pref)
        
        result.append(NotificationPreferenceResponse(
            id=pref.id,
            notification_type=pref.notification_type,
            channel_push=pref.channel_push,
            channel_sms=pref.channel_sms,
            channel_email=pref.channel_email,
            store_filter_id=pref.store_filter_id
        ))
    
    return result


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    user_id: int,
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get notifications for a user.
    
    - **user_id**: User to get notifications for
    - **unread_only**: Only return unread notifications
    - **limit**: Maximum number to return
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    return [NotificationResponse(
        id=n.id,
        notification_type=n.notification_type,
        title=n.title,
        message=n.message,
        is_read=n.is_read,
        created_at=n.created_at.isoformat()
    ) for n in notifications]


@router.post("/{notification_id}/read", response_model=dict)
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Notification marked as read"}


@router.post("/send", response_model=dict, status_code=status.HTTP_201_CREATED)
async def send_notification(
    request: SendNotificationRequest,
    db: Session = Depends(get_db)
):
    """
    Send a notification to a user.
    
    This is an internal endpoint for the system to send notifications.
    It checks user preferences and sends through appropriate channels.
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user preferences for this notification type
    pref = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == request.user_id,
        NotificationPreference.notification_type == request.notification_type
    ).first()
    
    # Default preferences if not set
    send_push = True
    send_sms = request.notification_type == "UNPAID_EXIT"  # Security alerts default to SMS
    send_email = request.notification_type == "UNPAID_EXIT"
    
    if pref:
        send_push = pref.channel_push
        send_sms = pref.channel_sms
        send_email = pref.channel_email
    
    # Create notification record
    notification = Notification(
        user_id=request.user_id,
        notification_type=request.notification_type,
        title=request.title,
        message=request.message,
        sent_push=send_push,
        sent_sms=send_sms,
        sent_email=send_email,
        store_id=request.store_id,
        tag_epc=request.tag_epc
    )
    
    db.add(notification)
    db.commit()
    
    # TODO: Actually send through channels
    # - Push: Use Firebase Cloud Messaging
    # - SMS: Use Twilio/MessageBird
    # - Email: Use SendGrid/AWS SES
    
    channels_sent = []
    if send_push:
        channels_sent.append("push")
    if send_sms:
        channels_sent.append("sms")
    if send_email:
        channels_sent.append("email")
    
    return {
        "message": "Notification sent",
        "channels": channels_sent,
        "notification_id": notification.id
    }
