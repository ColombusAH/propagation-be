"""
Exit gate scanning API - triggers security alerts for unpaid items.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.rfid_tag import RFIDTag
from app.models.store import Notification, NotificationPreference, Store, User
from app.services.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exit-scan", tags=["exit-scan"])


# ============= Pydantic Schemas =============


class ExitScanRequest(BaseModel):
    """Request for scanning tags at exit gate."""

    epcs: List[str]  # List of EPC codes scanned at exit
    gate_id: str = "main-exit"  # Which exit gate
    store_id: Optional[int] = None


class UnpaidItemAlert(BaseModel):
    """Alert for a single unpaid item."""

    epc: str
    product_name: Optional[str]
    product_sku: Optional[str]
    price_cents: Optional[int]
    price_display: str


class ExitScanResponse(BaseModel):
    """Response from exit scan."""

    total_scanned: int
    paid_count: int
    unpaid_count: int
    unpaid_items: List[UnpaidItemAlert]
    alert_sent: bool
    alert_recipients: int


# ============= API Endpoints =============


@router.post("/check", response_model=ExitScanResponse)
async def check_exit_scan(request: ExitScanRequest, db: Session = Depends(get_db)):
    """
    Check tags scanned at exit gate for unpaid items.

    This is called when RFID reader at exit gate detects tags.
    If any tag has is_paid=False, triggers UNPAID_EXIT notifications
    to all store stakeholders.

    Flow:
    1. Receive list of EPCs from exit gate reader
    2. Check each tag's payment status
    3. If unpaid items found:
       a. Get all store stakeholders (managers, sellers)
       b. Send notification to each based on their preferences
       c. Log the security event
    4. Return summary with unpaid items list
    """

    unpaid_items: List[UnpaidItemAlert] = []
    paid_count = 0

    for epc in request.epcs:
        tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()

        if not tag:
            # Unknown tag - treat as suspicious
            unpaid_items.append(
                UnpaidItemAlert(
                    epc=epc,
                    product_name="מוצר לא מזוהה",
                    product_sku=None,
                    price_cents=None,
                    price_display="לא ידוע",
                )
            )
            continue

        if tag.is_paid:
            paid_count += 1
        else:
            # Unpaid item!
            price_display = f"₪{tag.price_cents / 100:.2f}" if tag.price_cents else "לא ידוע"
            unpaid_items.append(
                UnpaidItemAlert(
                    epc=epc,
                    product_name=tag.product_name or "ללא שם",
                    product_sku=tag.product_sku,
                    price_cents=tag.price_cents,
                    price_display=price_display,
                )
            )

    alert_sent = False
    alert_recipients = 0

    # If there are unpaid items, send alerts
    if unpaid_items:
        store_id = request.store_id

        # Get all stakeholders for this store
        stakeholders = db.query(User).filter(
            User.is_active.is_(True), User.role.in_(["ADMIN", "MANAGER", "SELLER"])
        )

        if store_id:
            # For MANAGER and SELLER, filter by store
            # ADMIN gets all notifications
            stakeholders = stakeholders.filter((User.store_id == store_id) | (User.role == "ADMIN"))

        stakeholders = stakeholders.all()

        # Build alert message
        items_text = "\n".join(
            [f"- {item.product_name} ({item.epc}) | {item.price_display}" for item in unpaid_items]
        )

        message = f"זוהו {len(unpaid_items)} פריטים לא משולמים בשער יציאה!\n\n"
        message += f"שער: {request.gate_id}\n"
        if store_id:
            store = db.query(Store).filter(Store.id == store_id).first()
            if store:
                message += f"חנות: {store.name}\n"
        message += f"\nפריטים:\n{items_text}"

        # Send notification to each stakeholder
        for user in stakeholders:
            # Check user preferences
            pref = (
                db.query(NotificationPreference)
                .filter(
                    NotificationPreference.user_id == user.id,
                    NotificationPreference.notification_type == "UNPAID_EXIT",
                )
                .first()
            )

            # Default: all channels for security alerts
            send_push = True
            send_sms = True
            send_email = True

            if pref:
                send_push = pref.channel_push
                send_sms = pref.channel_sms
                send_email = pref.channel_email

            # Create notification record
            notification = Notification(
                user_id=user.id,
                notification_type="UNPAID_EXIT",
                title="⚠️ מוצר לא שולם ביציאה",
                message=message,
                sent_push=send_push,
                sent_sms=send_sms,
                sent_email=send_email,
                store_id=store_id,
                tag_epc=unpaid_items[0].epc if unpaid_items else None,
            )
            db.add(notification)

            # TODO: Actually send via channels:
            # - Push: Firebase Cloud Messaging
            # - SMS: Twilio / MessageBird
            # - Email: SendGrid / AWS SES

            alert_recipients += 1
            logger.warning(
                f"SECURITY ALERT: Unpaid items detected! "
                f"User: {user.name}, Items: {len(unpaid_items)}"
            )

        db.commit()
        alert_sent = True

        logger.error(
            f"UNPAID EXIT ALERT: {len(unpaid_items)} unpaid items at gate {request.gate_id}"
        )

    return ExitScanResponse(
        total_scanned=len(request.epcs),
        paid_count=paid_count,
        unpaid_count=len(unpaid_items),
        unpaid_items=unpaid_items,
        alert_sent=alert_sent,
        alert_recipients=alert_recipients,
    )


@router.post("/mark-paid")
async def mark_tags_as_paid(epcs: List[str], db: Session = Depends(get_db)):
    """
    Mark tags as paid after checkout.

    Called after successful payment to update tag status.
    """
    from datetime import datetime, timezone

    updated = 0
    for epc in epcs:
        tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()
        if tag:
            tag.is_paid = True
            tag.paid_at = datetime.now(timezone.utc)
            updated += 1

    db.commit()

    return {
        "message": f"Marked {updated} tags as paid",
        "updated_count": updated,
        "total_requested": len(epcs),
    }


@router.post("/mark-unpaid")
async def mark_tags_as_unpaid(epcs: List[str], db: Session = Depends(get_db)):
    """
    Mark tags as unpaid (for returns or restocking).
    """
    updated = 0
    for epc in epcs:
        tag = db.query(RFIDTag).filter(RFIDTag.epc == epc).first()
        if tag:
            tag.is_paid = False
            tag.paid_at = None
            updated += 1

    db.commit()

    return {"message": f"Marked {updated} tags as unpaid", "updated_count": updated}
