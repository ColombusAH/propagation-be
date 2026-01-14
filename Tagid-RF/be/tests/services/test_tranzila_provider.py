"""
Tests for Tranzila Payment Provider - Mocked HTTP responses.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.payment_provider import PaymentStatus


@pytest.fixture
def tranzila_provider():
    """Create TranzilaProvider with mocked settings."""
    with patch("app.services.tranzila_provider.settings") as mock_settings:
        mock_settings.TRANZILA_TERMINAL_NAME = "test_terminal"
        mock_settings.TRANZILA_API_KEY = "test_key"
        mock_settings.TRANZILA_API_ENDPOINT = "https://test.tranzila.com"
        
        from app.services.tranzila_provider import TranzilaProvider
        provider = TranzilaProvider()
        return provider


@pytest.mark.asyncio
async def test_create_payment_intent_success(tranzila_provider):
    """Test successful payment intent creation."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Response=000&ConfirmationCode=12345"
    
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        mock_client_cls.return_value = mock_client
        
        result = await tranzila_provider.create_payment_intent(
            amount=1000,
            currency="ILS"
        )
        
        assert result["status"] == PaymentStatus.PENDING
        assert "payment_id" in result


@pytest.mark.asyncio
async def test_confirm_payment(tranzila_provider):
    """Test payment confirmation."""
    # First create a transaction
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Response=000"
    
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        mock_client_cls.return_value = mock_client
        
        # Create a transaction first
        create_result = await tranzila_provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        
        # Confirm it
        confirm_result = await tranzila_provider.confirm_payment(payment_id)
        
        assert confirm_result["status"] == PaymentStatus.COMPLETED


@pytest.mark.asyncio
async def test_confirm_payment_not_found(tranzila_provider):
    """Test confirming non-existent payment."""
    with pytest.raises(ValueError, match="not found"):
        await tranzila_provider.confirm_payment("nonexistent_id")


@pytest.mark.asyncio
async def test_cancel_payment(tranzila_provider):
    """Test payment cancellation."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Response=000"
    
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        mock_client_cls.return_value = mock_client
        
        # Create a transaction first
        create_result = await tranzila_provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        
        # Cancel it
        cancel_result = await tranzila_provider.cancel_payment(payment_id)
        
        assert cancel_result["status"] == PaymentStatus.FAILED


@pytest.mark.asyncio
async def test_get_payment_status(tranzila_provider):
    """Test getting payment status."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Response=000"
    
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock()
        mock_client_cls.return_value = mock_client
        
        # Create a transaction first
        create_result = await tranzila_provider.create_payment_intent(1000, "ILS")
        payment_id = create_result["payment_id"]
        
        # Get status
        status = await tranzila_provider.get_payment_status(payment_id)
        
        assert status == PaymentStatus.PENDING
