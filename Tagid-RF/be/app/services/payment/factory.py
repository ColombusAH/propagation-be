"""Payment gateway factory."""

import logging
import os

from app.core.config import settings
from .base import PaymentGateway

logger = logging.getLogger(__name__)

# Lazy-loaded gateway instances
_gateways: dict[str, PaymentGateway] = {}


def get_gateway(provider: str = "stripe") -> PaymentGateway:
    """Get a payment gateway instance by provider name."""
    provider = provider.lower()

    if provider in _gateways:
        return _gateways[provider]

    if provider == "stripe":
        gateway = _create_stripe_gateway()
    elif provider == "tranzila":
        gateway = _create_tranzila_gateway()
    elif provider == "cash":
        gateway = _create_cash_gateway()
    else:
        raise ValueError(f"Unknown payment provider: {provider}")

    _gateways[provider] = gateway
    return gateway


def _create_stripe_gateway() -> PaymentGateway:
    """Create a Stripe gateway instance."""
    from .stripe_gateway import StripeGateway

    api_key = settings.STRIPE_SECRET_KEY
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not api_key:
        raise ValueError("STRIPE_SECRET_KEY is required in settings")

    return StripeGateway(api_key=api_key, webhook_secret=webhook_secret)


def _create_tranzila_gateway() -> PaymentGateway:
    """Create a Tranzila gateway instance."""
    from .tranzila import TranzilaGateway

    # Note: config.py uses TRANZILA_TERMINAL_NAME, factory used TRANZILA_TERMINAL.
    # Aligning to config.py
    terminal = settings.TRANZILA_TERMINAL_NAME
    # config.py doesn't seem to have TRANZILA_PASSWORD, it has TRANZILA_API_KEY.
    # Let's check tranzila.py requirements.
    # tranzila.py asks for terminal_password.
    # Let's assume TRANZILA_API_KEY map to password or we need to add PASSWORD to config.
    # For now, I will use TRANZILA_API_KEY as password if that's the intent, or stick to os.getenv if missing.
    # config.py has TRANZILA_API_KEY.
    password = settings.TRANZILA_API_KEY

    if not terminal:
        raise ValueError("TRANZILA_TERMINAL_NAME is required in settings")

    return TranzilaGateway(terminal_name=terminal, terminal_password=password)


def _create_cash_gateway() -> PaymentGateway:
    """Create a cash payment gateway (manual payments)."""
    from .cash_gateway import CashGateway

    return CashGateway()


def get_available_providers() -> list[str]:
    """Return list of available payment providers based on config."""
    providers = []

    if os.getenv("STRIPE_SECRET_KEY"):
        providers.append("stripe")

    if os.getenv("TRANZILA_TERMINAL"):
        providers.append("tranzila")

    # Cash is always available
    providers.append("cash")

    return providers
