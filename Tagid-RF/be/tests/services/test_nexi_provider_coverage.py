"""
Tests for NexiProvider payment service.
Covers: __init__, create_payment_intent, confirm_payment, refund_payment, get_payment_status, cancel_payment
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestNexiProvider:
    """Tests for NexiProvider."""

    @pytest.fixture
    def provider(self):
        """Create NexiProvider instance with mocked settings."""
        with patch("app.services.nexi_provider.settings") as mock_settings:
            mock_settings.NEXI_TERMINAL_ID = "test_terminal"
            mock_settings.NEXI_API_KEY = "test_api_key"
            mock_settings.NEXI_API_ENDPOINT = "https://test.nexi.co.il"
            mock_settings.NEXI_MERCHANT_ID = "test_merchant"

            from app.services.nexi_provider import NexiProvider

            return NexiProvider()

    def test_init(self, provider):
        """Test provider initialization."""
        assert provider is not None
        assert provider.terminal_id == "test_terminal"
        assert provider.pending_transactions == {}

    @pytest.mark.asyncio
    async def test_create_payment_intent(self, provider):
        """Test creating a payment intent."""
        with patch("app.services.nexi_provider.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "transaction_id": "nexi_123",
                "status": "pending",
            }
            mock_cm = MagicMock()
            mock_cm.__aenter__ = AsyncMock(
                return_value=MagicMock(post=AsyncMock(return_value=mock_response))
            )
            mock_cm.__aexit__ = AsyncMock()
            mock_client.return_value = mock_cm

            result = await provider.create_payment_intent(1000, "ILS", {"order": "123"})

            assert "payment_id" in result
            assert result["status"].value == "PENDING"

    @pytest.mark.asyncio
    async def test_create_payment_intent_error(self, provider):
        """Test handling API error during payment creation."""
        with patch("app.services.nexi_provider.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"
            mock_cm = MagicMock()
            mock_cm.__aenter__ = AsyncMock(
                return_value=MagicMock(post=AsyncMock(return_value=mock_response))
            )
            mock_cm.__aexit__ = AsyncMock()
            mock_client.return_value = mock_cm

            with pytest.raises(ValueError):
                await provider.create_payment_intent(1000, "ILS")

    @pytest.mark.asyncio
    async def test_confirm_payment(self, provider):
        """Test confirming a payment."""
        # First add transaction to pending
        from app.services.nexi_provider import PaymentStatus

        provider.pending_transactions["txn-123"] = {
            "amount": 1000,
            "currency": "ILS",
            "status": PaymentStatus.PENDING,
            "metadata": {},
        }

        with patch("app.services.nexi_provider.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "completed"}
            mock_cm = MagicMock()
            mock_cm.__aenter__ = AsyncMock(
                return_value=MagicMock(post=AsyncMock(return_value=mock_response))
            )
            mock_cm.__aexit__ = AsyncMock()
            mock_client.return_value = mock_cm

            result = await provider.confirm_payment("txn-123")

            assert "status" in result

    @pytest.mark.asyncio
    async def test_confirm_payment_not_found(self, provider):
        """Test confirming a non-existent payment."""
        with pytest.raises(ValueError, match="not found"):
            await provider.confirm_payment("nonexistent")

    @pytest.mark.asyncio
    async def test_refund_payment(self, provider):
        """Test refunding a payment."""
        from app.services.nexi_provider import PaymentStatus

        provider.pending_transactions["txn-123"] = {
            "amount": 1000,
            "currency": "ILS",
            "status": PaymentStatus.COMPLETED,
            "metadata": {},
        }

        with patch("app.services.nexi_provider.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"refund_id": "ref-123", "amount": 500}
            mock_cm = MagicMock()
            mock_cm.__aenter__ = AsyncMock(
                return_value=MagicMock(post=AsyncMock(return_value=mock_response))
            )
            mock_cm.__aexit__ = AsyncMock()
            mock_client.return_value = mock_cm

            result = await provider.refund_payment("txn-123", 500)

            assert "refund_id" in result

    @pytest.mark.asyncio
    async def test_get_payment_status(self, provider):
        """Test getting payment status."""
        from app.services.nexi_provider import PaymentStatus

        provider.pending_transactions["txn-123"] = {"status": PaymentStatus.COMPLETED}

        result = await provider.get_payment_status("txn-123")

        assert result == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_cancel_payment(self, provider):
        """Test cancelling a payment."""
        from app.services.nexi_provider import PaymentStatus

        provider.pending_transactions["txn-123"] = {
            "amount": 1000,
            "currency": "ILS",
            "status": PaymentStatus.PENDING,
            "metadata": {},
        }

        with patch("app.services.nexi_provider.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "cancelled"}
            mock_cm = MagicMock()
            mock_cm.__aenter__ = AsyncMock(
                return_value=MagicMock(post=AsyncMock(return_value=mock_response))
            )
            mock_cm.__aexit__ = AsyncMock()
            mock_client.return_value = mock_cm

            result = await provider.cancel_payment("txn-123")

            assert "status" in result

    @pytest.mark.asyncio
    async def test_cancel_non_pending_fails(self, provider):
        """Test cancelling a non-pending payment fails."""
        from app.services.nexi_provider import PaymentStatus

        provider.pending_transactions["txn-123"] = {"status": PaymentStatus.COMPLETED}

        with pytest.raises(ValueError, match="Cannot cancel"):
            await provider.cancel_payment("txn-123")
