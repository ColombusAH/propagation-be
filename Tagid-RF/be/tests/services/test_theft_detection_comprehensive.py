"""
Tests for Theft Detection Service.
Covers tag payment checking, alert creation, and notification logic.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.theft_detection import TheftDetectionService


@pytest.fixture
def service():
    return TheftDetectionService()


@pytest.fixture
def mock_prisma():
    with patch("app.services.theft_detection.prisma_client") as mock:
        mock.client = MagicMock()
        yield mock


@pytest.mark.asyncio
async def test_check_tag_paid(service, mock_prisma):
    """Test that paid tags return True and don't create alerts."""
    mock_prisma.client.tagmapping.find_unique = AsyncMock(
        return_value=MagicMock(isPaid=True, epc="E200001234")
    )

    result = await service.check_tag_payment_status("E200001234")
    assert result is True


@pytest.mark.asyncio
async def test_check_tag_unpaid_creates_alert(service, mock_prisma):
    """Test that unpaid tags return False and trigger alert creation."""
    mock_tag = MagicMock(
        id="tag-123",
        epc="E200001234",
        isPaid=False,
        productDescription="Test Product",
    )
    mock_prisma.client.tagmapping.find_unique = AsyncMock(return_value=mock_tag)
    mock_prisma.client.theftalert.create = AsyncMock(return_value=MagicMock(id="alert-1"))
    mock_prisma.client.user.find_many = AsyncMock(return_value=[])

    result = await service.check_tag_payment_status("E200001234", location="Exit Gate")
    assert result is False
    mock_prisma.client.theftalert.create.assert_called_once()


@pytest.mark.asyncio
async def test_check_tag_not_found(service, mock_prisma):
    """Test that unknown tags return True (no alert)."""
    mock_prisma.client.tagmapping.find_unique = AsyncMock(return_value=None)

    result = await service.check_tag_payment_status("UNKNOWN_EPC")
    assert result is True


@pytest.mark.asyncio
async def test_resolve_alert_success(service, mock_prisma):
    """Test resolving a theft alert."""
    mock_prisma.client.theftalert.update = AsyncMock(return_value=MagicMock(id="alert-1"))

    await service.resolve_alert("alert-1", resolved_by="user-123", notes="False alarm")
    mock_prisma.client.theftalert.update.assert_called_once()


@pytest.mark.asyncio
async def test_resolve_alert_error(service, mock_prisma):
    """Test error handling when resolving alert fails."""
    mock_prisma.client.theftalert.update = AsyncMock(side_effect=Exception("DB Error"))

    with pytest.raises(Exception, match="DB Error"):
        await service.resolve_alert("alert-1", resolved_by="user-123")


def test_create_alert_message(service):
    """Test alert message formatting."""
    mock_tag = MagicMock(epc="E200001234", productDescription="Blue T-Shirt")
    message = service._create_alert_message(mock_tag)
    assert "E200001234" in message
    assert "Blue T-Shirt" in message


def test_create_alert_message_no_description(service):
    """Test alert message with no product description."""
    mock_tag = MagicMock(epc="E200001234", productDescription=None)
    message = service._create_alert_message(mock_tag)
    assert "לא ידוע" in message
