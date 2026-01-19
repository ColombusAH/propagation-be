"""
Comprehensive tests for Nexi Payment Provider.
Covers payment creation, confirmation, refund, and cancellation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.nexi_provider import NexiProvider
from app.services.payment_provider import PaymentStatus


@pytest.fixture
def provider():
    """Create Nexi provider with mocked settings."""
    with patch("app.services.nexi_provider.settings") as mock_settings:
        mock_settings.NEXI_TERMINAL_ID = "test_terminal"
        mock_settings.NEXI_API_KEY = "test_api_key"
        mock_settings.NEXI_API_ENDPOINT = "https://api.nexi.test"
        mock_settings.NEXI_MERCHANT_ID = "test_merchant"
        return NexiProvider()


# --- Initialization Tests ---
def test_nexi_provider_init(provider):
    """Test NexiProvider initialization."""
    assert provider.terminal_id == "test_terminal"
    assert provider.api_key == "test_api_key"
    assert provider.pending_transactions == {}


# --- Create Payment Tests ---
@pytest.mark.asyncio
async def test_create_payment_success(provider):
    """Test successful payment creation."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"transaction_id": "nexi_123"}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await provider.create_payment_intent(5000, "ILS", {"order": "test"})

        assert "payment_id" in result
        assert result["status"] == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_create_payment_api_error(provider):
    """Test payment creation with API error."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with pytest.raises(ValueError, match="Failed to create"):
            await provider.create_payment_intent(5000, "ILS")


# --- Confirm Payment Tests ---
@pytest.mark.asyncio
async def test_confirm_payment_not_found(provider):
    """Test confirm payment with unknown transaction."""
    with pytest.raises(ValueError, match="not found"):
        await provider.confirm_payment("unknown_id")


@pytest.mark.asyncio
async def test_confirm_payment_success(provider):
    """Test successful payment confirmation."""
    provider.pending_transactions["test_id"] = {
        "amount": 5000,
        "currency": "ILS",
        "status": PaymentStatus.PENDING,
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "completed"}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await provider.confirm_payment("test_id")

        assert result["status"] == PaymentStatus.COMPLETED


# --- Get Payment Status Tests ---
@pytest.mark.asyncio
async def test_get_payment_status_not_found(provider):
    """Test get status with unknown transaction."""
    with pytest.raises(ValueError, match="not found"):
        await provider.get_payment_status("unknown_id")


@pytest.mark.asyncio
async def test_get_payment_status_success(provider):
    """Test get payment status success."""
    provider.pending_transactions["test_id"] = {
        "amount": 5000,
        "status": PaymentStatus.COMPLETED,
    }

    status = await provider.get_payment_status("test_id")
    assert status == PaymentStatus.COMPLETED


# --- Refund Payment Tests ---
@pytest.mark.asyncio
async def test_refund_payment_not_found(provider):
    """Test refund with unknown transaction."""
    with pytest.raises(ValueError, match="not found"):
        await provider.refund_payment("unknown_id")


@pytest.mark.asyncio
async def test_refund_payment_success(provider):
    """Test successful refund."""
    provider.pending_transactions["test_id"] = {
        "amount": 5000,
        "currency": "ILS",
        "status": PaymentStatus.COMPLETED,
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"refund_id": "refund_123"}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await provider.refund_payment("test_id", 2500)

        assert result["status"] == PaymentStatus.REFUNDED
        assert result["amount"] == 2500


# --- Cancel Payment Tests ---
@pytest.mark.asyncio
async def test_cancel_payment_not_found(provider):
    """Test cancel with unknown transaction."""
    with pytest.raises(ValueError, match="not found"):
        await provider.cancel_payment("unknown_id")


@pytest.mark.asyncio
async def test_cancel_payment_not_pending(provider):
    """Test cancel payment that's already completed."""
    provider.pending_transactions["test_id"] = {
        "amount": 5000,
        "status": PaymentStatus.COMPLETED,
    }

    with pytest.raises(ValueError, match="Cannot cancel"):
        await provider.cancel_payment("test_id")


@pytest.mark.asyncio
async def test_cancel_payment_success(provider):
    """Test successful payment cancellation."""
    provider.pending_transactions["test_id"] = {
        "amount": 5000,
        "status": PaymentStatus.PENDING,
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await provider.cancel_payment("test_id")

        assert result["status"] == PaymentStatus.FAILED
