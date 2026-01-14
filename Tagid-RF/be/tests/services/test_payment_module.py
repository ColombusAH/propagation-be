"""
Tests for Payment Module - Base class, Factory, and Gateways.
Simple import and structure tests.
"""

import os
from unittest.mock import patch

import pytest


class TestPaymentImports:
    """Tests for payment module imports."""

    def test_import_payment_base(self):
        """Test payment base imports correctly."""
        from app.services.payment import base

        assert base is not None

    def test_import_factory(self):
        """Test factory imports correctly."""
        from app.services.payment import factory

        assert factory is not None

    def test_import_cash_gateway(self):
        """Test cash gateway imports correctly."""
        from app.services.payment import cash_gateway

        assert cash_gateway is not None

    def test_import_stripe_gateway(self):
        """Test stripe gateway imports correctly."""
        from app.services.payment import stripe_gateway

        assert stripe_gateway is not None

    def test_import_tranzila(self):
        """Test tranzila imports correctly."""
        from app.services.payment import tranzila

        assert tranzila is not None


class TestPaymentBase:
    """Tests for PaymentGateway base class."""

    def test_base_class_exists(self):
        """Test base class can be imported."""
        from app.services.payment.base import PaymentGateway

        assert PaymentGateway is not None

    def test_payment_status_enum(self):
        """Test PaymentStatus enum exists in base."""
        from app.services.payment.base import PaymentStatus

        assert PaymentStatus is not None


class TestPaymentFactory:
    """Tests for payment factory functions."""

    def test_get_gateway_function_exists(self):
        """Test get_gateway function exists."""
        from app.services.payment.factory import get_gateway

        assert get_gateway is not None

    def test_get_available_providers(self):
        """Test get_available_providers function."""
        from app.services.payment.factory import get_available_providers

        providers = get_available_providers()

        # Cash should always be available
        assert "cash" in providers

    def test_get_cash_gateway(self):
        """Test getting cash gateway."""
        from app.services.payment.factory import get_gateway

        gateway = get_gateway("cash")
        assert gateway is not None

    def test_invalid_provider_raises_error(self):
        """Test invalid provider raises ValueError."""
        from app.services.payment.factory import get_gateway

        with pytest.raises(ValueError, match="Unknown payment provider"):
            get_gateway("invalid_provider_xyz")
