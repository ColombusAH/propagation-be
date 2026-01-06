"""Payment gateway factory."""

import logging
import os

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

    api_key = os.getenv("STRIPE_SECRET_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not api_key:
        raise ValueError("STRIPE_SECRET_KEY environment variable is required")

    return StripeGateway(api_key=api_key, webhook_secret=webhook_secret)


def _create_tranzila_gateway() -> PaymentGateway:
    """Create a Tranzila gateway instance."""
    from .tranzila import TranzilaGateway

    terminal = os.getenv("TRANZILA_TERMINAL")
    password = os.getenv("TRANZILA_PASSWORD")

    if not terminal:
        raise ValueError("TRANZILA_TERMINAL environment variable is required")

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
