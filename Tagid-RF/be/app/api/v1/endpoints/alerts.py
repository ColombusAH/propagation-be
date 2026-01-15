"""
Alerts API endpoints.
Handles theft alert management and notifications.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.permissions import requires_any_role
from app.db.prisma import prisma_client
from app.services.theft_detection import TheftDetectionService

logger = logging.getLogger(__name__)
router = APIRouter()

theft_service = TheftDetectionService()


# Schemas
class TheftAlertResponse(BaseModel):
    id: str
    epc: str
    productDescription: Optional[str]
    detectedAt: datetime
    location: Optional[str]
    resolved: bool
    resolvedAt: Optional[datetime]
    resolvedBy: Optional[str]
    notes: Optional[str]


class ResolveAlertRequest(BaseModel):
    notes: Optional[str] = None


class MarkReadRequest(BaseModel):
    alert_id: str


@router.get("/", response_model=List[TheftAlertResponse])
async def list_theft_alerts(
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    current_user=Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER"])),
):
    """
    List theft alerts (STORE_MANAGER+ only).

    - **resolved**: Filter by resolved status
    - **limit**: Maximum number of results
    - **offset**: Pagination offset
    """
    try:
        where_clause = {}
        if resolved is not None:
            where_clause["resolved"] = resolved

        alerts = await prisma_client.client.theftalert.find_many(
            where=where_clause, order_by={"detectedAt": "desc"}, take=limit, skip=offset
        )

        return [
            TheftAlertResponse(
                id=alert.id,
                epc=alert.epc,
                productDescription=alert.productDescription,
                detectedAt=alert.detectedAt,
                location=alert.location,
                resolved=alert.resolved,
                resolvedAt=alert.resolvedAt,
                resolvedBy=alert.resolvedBy,
                notes=alert.notes,
            )
            for alert in alerts
        ]

    except Exception as e:
        logger.error(f"Error listing alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list alerts: {str(e)}",
        )


@router.get("/my-alerts", response_model=List[TheftAlertResponse])
async def get_my_alerts(
    unread_only: bool = Query(False),
    limit: int = Query(50, le=100),
    current_user=Depends(get_current_user),
):
    """
    Get alerts sent to current user.

    - **unread_only**: Show only unread alerts
    - **limit**: Maximum number of results
    """
    try:
        where_clause = {"userId": current_user.id}
        if unread_only:
            where_clause["read"] = False

        recipients = await prisma_client.client.alertrecipient.find_many(
            where=where_clause,
            include={"theftAlert": True},
            order_by={"sentAt": "desc"},
            take=limit,
        )

        return [
            TheftAlertResponse(
                id=recipient.theftAlert.id,
                epc=recipient.theftAlert.epc,
                productDescription=recipient.theftAlert.productDescription,
                detectedAt=recipient.theftAlert.detectedAt,
                location=recipient.theftAlert.location,
                resolved=recipient.theftAlert.resolved,
                resolvedAt=recipient.theftAlert.resolvedAt,
                resolvedBy=recipient.theftAlert.resolvedBy,
                notes=recipient.theftAlert.notes,
            )
            for recipient in recipients
        ]

    except Exception as e:
        logger.error(f"Error getting user alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user alerts: {str(e)}",
        )


@router.get("/{alert_id}", response_model=TheftAlertResponse)
async def get_alert_details(
    alert_id: str,
    current_user=Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER"])),
):
    """
    Get theft alert details (STORE_MANAGER+ only).

    - **alert_id**: Alert ID
    """
    try:
        alert = await prisma_client.client.theftalert.find_unique(where={"id": alert_id})

        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

        return TheftAlertResponse(
            id=alert.id,
            epc=alert.epc,
            productDescription=alert.productDescription,
            detectedAt=alert.detectedAt,
            location=alert.location,
            resolved=alert.resolved,
            resolvedAt=alert.resolvedAt,
            resolvedBy=alert.resolvedBy,
            notes=alert.notes,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get alert: {str(e)}",
        )


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    request: ResolveAlertRequest,
    current_user=Depends(requires_any_role(["SUPER_ADMIN", "NETWORK_MANAGER", "STORE_MANAGER"])),
):
    """
    Mark theft alert as resolved (STORE_MANAGER+ only).

    - **alert_id**: Alert ID
    - **notes**: Resolution notes
    """
    try:
        await theft_service.resolve_alert(
            alert_id=alert_id, resolved_by=current_user.id, notes=request.notes
        )

        return {"message": "Alert resolved successfully"}

    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve alert: {str(e)}",
        )


@router.post("/mark-read/{alert_id}")
async def mark_alert_read(alert_id: str, current_user=Depends(get_current_user)):
    """
    Mark an alert as read.

    - **alert_id**: Alert ID
    """
    try:
        # Find recipient record for this user and alert
        recipient = await prisma_client.client.alertrecipient.find_first(
            where={"AND": [{"theftAlertId": alert_id}, {"userId": current_user.id}]}
        )

        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found for this user"
            )

        # Mark as read
        await prisma_client.client.alertrecipient.update(
            where={"id": recipient.id}, data={"read": True, "readAt": datetime.now()}
        )

        return {"message": "Alert marked as read"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking alert as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark alert as read: {str(e)}",
        )
