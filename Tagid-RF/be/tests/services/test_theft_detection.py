"""
Tests for TheftDetectionService - Mocked tests for alert lifecycle.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.theft_detection import TheftDetectionService


@pytest.fixture
def theft_service():
    with patch("app.services.theft_detection.PushNotificationService"):
        return TheftDetectionService()


@pytest.fixture
def mock_tag():
    tag = MagicMock()
    tag.id = "tag_123"
    tag.epc = "E200UNPAID"
    tag.isPaid = False
    tag.productDescription = "Test Watch"
    return tag


@pytest.mark.asyncio
async def test_check_tag_paid_returns_true(theft_service):
    """Paid tags should return True and not create alert."""
    mock_tag = MagicMock()
    mock_tag.isPaid = True
    mock_tag.epc = "E200PAID"

    with patch("app.services.theft_detection.prisma_client") as mock_prisma:
        mock_prisma.client.rfidtag.find_unique = AsyncMock(return_value=mock_tag)

        result = await theft_service.check_tag_payment_status("E200PAID")

        assert result is True


@pytest.mark.asyncio
async def test_check_tag_unpaid_returns_false(theft_service, mock_tag):
    """Unpaid tags should return False and trigger alert."""
    with patch("app.services.theft_detection.prisma_client") as mock_prisma:
        mock_prisma.client.rfidtag.find_unique = AsyncMock(return_value=mock_tag)
        mock_prisma.client.theftalert.create = AsyncMock(return_value=MagicMock(id="alert_1"))
        mock_prisma.client.user.find_many = AsyncMock(return_value=[])

        result = await theft_service.check_tag_payment_status("E200UNPAID", location="Gate 1")

        assert result is False
        mock_prisma.client.theftalert.create.assert_called_once()


@pytest.mark.asyncio
async def test_check_unknown_tag_returns_true(theft_service):
    """Unknown tags should return True (don't alert on unknowns)."""
    with patch("app.services.theft_detection.prisma_client") as mock_prisma:
        mock_prisma.client.tagmapping.find_unique = AsyncMock(return_value=None)

        result = await theft_service.check_tag_payment_status("UNKNOWN_EPC")

        assert result is True


@pytest.mark.asyncio
async def test_create_alert_message(theft_service, mock_tag):
    """Test alert message formatting."""
    message = theft_service._create_alert_message(mock_tag)

    assert mock_tag.epc in message
    assert mock_tag.productDescription in message


@pytest.mark.asyncio
async def test_create_alert_message_no_description(theft_service):
    """Test alert message with missing product description."""
    tag = MagicMock()
    tag.epc = "EPC_NO_DESC"
    tag.productDescription = None

    message = theft_service._create_alert_message(tag)

    assert "לא ידוע" in message  # Hebrew for "unknown"


@pytest.mark.asyncio
async def test_resolve_alert(theft_service):
    """Test resolving a theft alert."""
    with patch("app.services.theft_detection.prisma_client") as mock_prisma:
        mock_prisma.client.theftalert.update = AsyncMock()

        await theft_service.resolve_alert(
            alert_id="alert_123", resolved_by="user_456", notes="False alarm"
        )

        mock_prisma.client.theftalert.update.assert_called_once()
        call_args = mock_prisma.client.theftalert.update.call_args
        assert call_args[1]["data"]["resolved"] is True
        assert call_args[1]["data"]["resolvedBy"] == "user_456"


@pytest.mark.asyncio
async def test_notify_stakeholders(theft_service, mock_tag):
    """Test notification to stakeholders."""
    mock_alert = MagicMock(id="alert_1")
    mock_user = MagicMock(id="user_1", email="admin@test.com")

    with patch("app.services.theft_detection.prisma_client") as mock_prisma:
        mock_prisma.client.alertrecipient.create = AsyncMock(return_value=MagicMock(id="rec_1"))
        mock_prisma.client.alertrecipient.update = AsyncMock()

        # Mock push service
        theft_service.push_service.send_notification = AsyncMock(return_value=True)

        await theft_service._notify_stakeholders(mock_alert, mock_tag, [mock_user])

        theft_service.push_service.send_notification.assert_called_once()
        mock_prisma.client.alertrecipient.create.assert_called_once()
        mock_prisma.client.alertrecipient.update.assert_called_once()  # Delivery status update
