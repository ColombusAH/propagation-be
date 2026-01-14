"""
Tests for Nexi Provider Service.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestNexiProviderStructure:
    """Unit tests for NexiProvider - testing imports and structure."""

    def test_import_nexi_provider(self):
        """Test NexiProvider can be imported."""
        from app.services.nexi_provider import NexiProvider

        assert NexiProvider is not None

    def test_provider_has_required_methods(self):
        """Test provider has required PaymentProvider methods."""
        from app.services.nexi_provider import NexiProvider

        assert hasattr(NexiProvider, "create_payment_intent")
        assert hasattr(NexiProvider, "confirm_payment")
        assert hasattr(NexiProvider, "refund_payment")
        assert hasattr(NexiProvider, "get_payment_status")
        assert hasattr(NexiProvider, "cancel_payment")


class TestNexiProviderInit:
    """Tests for NexiProvider initialization."""

    def test_provider_init(self):
        """Test provider can be initialized."""
        with patch("app.services.nexi_provider.settings") as mock_settings:
            mock_settings.NEXI_TERMINAL_ID = "test_terminal"
            mock_settings.NEXI_API_KEY = "test_key"
            mock_settings.NEXI_API_ENDPOINT = "https://test.nexi.com"

            from app.services.nexi_provider import NexiProvider

            provider = NexiProvider()

            assert provider is not None
