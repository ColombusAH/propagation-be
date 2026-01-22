"""
Mock-based tests for Theft Detection service.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.services.theft_detection import TheftDetectionService
from tests.mock_utils import MockModel


class TestTheftDetectionServiceMock:
    """Tests for theft detection service using mocks."""

    @pytest.mark.asyncio
    @patch("app.services.theft_detection.PushNotificationService")
    @patch("app.services.theft_detection.prisma_client")
    async def test_check_tag_payment_status_paid(self, mock_prisma, mock_push):
        """Test checking payment status for a paid tag."""
        service = TheftDetectionService()

        tag = MockModel(id="t1", epc="E1", isPaid=True)
        mock_prisma.client.rfidtag.find_unique = AsyncMock(return_value=tag)

        is_paid = await service.check_tag_payment_status("E1")
        assert is_paid is True
        mock_prisma.client.theftalert.create.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.services.theft_detection.PushNotificationService")
    @patch("app.services.theft_detection.prisma_client")
    async def test_check_tag_payment_status_unpaid(self, mock_prisma, mock_push):
        """Test checking payment status for an unpaid tag (detects theft)."""
        service = TheftDetectionService()
        service.push_service.send_notification = AsyncMock(return_value=True)

        tag = MockModel(id="t1", epc="E1", isPaid=False, productDescription="Test Product")
        mock_prisma.client.rfidtag.find_unique = AsyncMock(return_value=tag)

        # Mock alert creation
        alert = MockModel(id="a1")
        mock_prisma.client.theftalert.create = AsyncMock(return_value=alert)

        # Mock stakeholder lookup
        user = MockModel(id="u1", email="admin@test.com")
        mock_prisma.client.user.find_many = AsyncMock(return_value=[user])

        # Mock recipient creation
        recipient = MockModel(id="r1")
        mock_prisma.client.alertrecipient.create = AsyncMock(return_value=recipient)
        mock_prisma.client.alertrecipient.update = AsyncMock()

        is_paid = await service.check_tag_payment_status("E1", location="Front Door")
        assert is_paid is False
        assert mock_prisma.client.theftalert.create.called
        assert service.push_service.send_notification.called

    @pytest.mark.asyncio
    @patch("app.services.theft_detection.prisma_client")
    async def test_resolve_alert(self, mock_prisma):
        """Test resolving a theft alert."""
        service = TheftDetectionService()
        mock_prisma.client.theftalert.update = AsyncMock()

        await service.resolve_alert("a1", "u1", "Resolved manually")
        mock_prisma.client.theftalert.update.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("app.services.theft_detection.prisma_client")
    async def test_check_tag_not_found(self, mock_prisma):
        """Test checking status for tag not in DB."""
        service = TheftDetectionService()
        mock_prisma.client.rfidtag.find_unique = AsyncMock(return_value=None)

        is_paid = await service.check_tag_payment_status("GHOST")
        assert is_paid is True  # Logic says return True (no alert) for unknown tags
