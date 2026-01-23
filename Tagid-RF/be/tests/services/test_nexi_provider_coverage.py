"""
Coverage tests for Nexi Provider.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.nexi_provider import NexiProvider
from app.services.payment_provider import PaymentStatus


class TestNexiProviderCoverage:

    def setup_method(self):
        self.provider = NexiProvider()
        # Pre-seed a transaction for some tests
        self.provider.pending_transactions["tx1"] = {
            "amount": 1000,
            "currency": "ILS",
            "status": PaymentStatus.PENDING,
            "created_at": "2023-01-01T00:00:00",
        }

    @patch("app.services.nexi_provider.httpx.AsyncClient")
    async def test_create_payment_intent_network_error(self, mock_client):
        """Test expected network/exception error handling."""
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx
        mock_client_ctx.post.side_effect = Exception("Network Error")

        with pytest.raises(ValueError) as exc:
            await self.provider.create_payment_intent(1000, "ILS")
        assert "Failed to create" in str(exc.value)

    @patch("app.services.nexi_provider.httpx.AsyncClient")
    async def test_create_payment_intent_api_error(self, mock_client):
        """Test API returning non-200 status."""
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx

        response = MagicMock()
        response.status_code = 400
        response.text = "Bad Request"
        mock_client_ctx.post.return_value = response

        with pytest.raises(ValueError) as exc:
            await self.provider.create_payment_intent(1000, "ILS")
        assert "Nexi API error: 400" in str(exc.value)

    async def test_confirm_payment_not_found(self):
        """Test confirm payment for unknown ID."""
        with pytest.raises(ValueError) as exc:
            await self.provider.confirm_payment("unknown")
        assert "not found" in str(exc.value)

    @patch("app.services.nexi_provider.httpx.AsyncClient")
    async def test_confirm_payment_network_error(self, mock_client):
        """Test confirm payment network error."""
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx
        mock_client_ctx.post.side_effect = Exception("Network Error")

        with pytest.raises(ValueError) as exc:
            await self.provider.confirm_payment("tx1")
        assert "Failed to confirm" in str(exc.value)

    @patch("app.services.nexi_provider.httpx.AsyncClient")
    async def test_confirm_payment_api_failure(self, mock_client):
        """Test confirm payment API failure."""
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx

        response = MagicMock()
        response.status_code = 500
        mock_client_ctx.post.return_value = response

        with pytest.raises(ValueError) as exc:
            await self.provider.confirm_payment("tx1")
        assert "confirmation failed: 500" in str(exc.value)

    async def test_refund_payment_not_found(self):
        """Test refund for unknown ID."""
        with pytest.raises(ValueError) as exc:
            await self.provider.refund_payment("unknown")
        assert "not found" in str(exc.value)

    @patch("app.services.nexi_provider.httpx.AsyncClient")
    async def test_refund_payment_network_error(self, mock_client):
        """Test refund network error."""
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx
        mock_client_ctx.post.side_effect = Exception("Network Error")

        with pytest.raises(ValueError) as exc:
            await self.provider.refund_payment("tx1")
        assert "Failed to create refund" in str(exc.value)

    @patch("app.services.nexi_provider.httpx.AsyncClient")
    async def test_refund_payment_api_failure(self, mock_client):
        """Test refund API failure."""
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx

        response = MagicMock()
        response.status_code = 400
        mock_client_ctx.post.return_value = response

        with pytest.raises(ValueError) as exc:
            await self.provider.refund_payment("tx1")
        assert "refund failed: 400" in str(exc.value)

    async def test_get_payment_status_not_found(self):
        """Test get status for unknown ID."""
        with pytest.raises(ValueError) as exc:
            await self.provider.get_payment_status("unknown")
        assert "not found" in str(exc.value)

    async def test_cancel_payment_not_found(self):
        """Test cancel for unknown ID."""
        with pytest.raises(ValueError) as exc:
            await self.provider.cancel_payment("unknown")
        assert "not found" in str(exc.value)

    async def test_cancel_payment_invalid_state(self):
        """Test cancel for non-pending transaction."""
        self.provider.pending_transactions["tx_done"] = {
            "status": PaymentStatus.COMPLETED
        }
        with pytest.raises(ValueError) as exc:
            await self.provider.cancel_payment("tx_done")
        assert "Cannot cancel" in str(exc.value)

    @patch("app.services.nexi_provider.httpx.AsyncClient")
    async def test_cancel_payment_network_error(self, mock_client):
        """Test cancel network error."""
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx
        mock_client_ctx.post.side_effect = Exception("Network Error")

        with pytest.raises(ValueError) as exc:
            await self.provider.cancel_payment("tx1")
        assert "Failed to cancel" in str(exc.value)

    @patch("app.services.nexi_provider.httpx.AsyncClient")
    async def test_cancel_payment_api_failure(self, mock_client):
        """Test cancel API failure."""
        mock_client_ctx = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_ctx

        response = MagicMock()
        response.status_code = 500
        mock_client_ctx.post.return_value = response

        with pytest.raises(ValueError) as exc:
            await self.provider.cancel_payment("tx1")
        assert "cancellation failed: 500" in str(exc.value)
