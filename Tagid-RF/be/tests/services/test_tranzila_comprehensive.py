"""
Tests for Tranzila Payment Gateway.
Covers payment creation, confirmation, refund, and callback parsing.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# --- Initialization Tests ---
def test_tranzila_gateway_init():
    """Test TranzilaGateway initialization."""
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(
        terminal_name="test_terminal", terminal_password="pass123"
    )
    assert gateway.terminal == "test_terminal"
    assert gateway.password == "pass123"
    assert gateway.use_redirect is True


def test_tranzila_gateway_provider():
    """Test TranzilaGateway returns correct provider."""
    from app.services.payment.base import PaymentProvider
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test")
    assert gateway.provider == PaymentProvider.TRANZILA


# --- Payment Creation Tests ---
@pytest.mark.asyncio
async def test_create_redirect_payment():
    """Test redirect payment creation generates URL."""
    from app.services.payment.base import PaymentRequest, PaymentStatus
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test_terminal", use_redirect=True)
    request = PaymentRequest(
        order_id="order-123",
        amount=5000,
        currency="ILS",
        customer_name="Test User",
        customer_email="test@example.com",
        return_url="https://example.com/return",
    )

    result = await gateway.create_payment(request)

    assert result.success is True
    assert result.payment_id == "order-123"
    assert "tranzila.com" in result.redirect_url
    assert "supplier=test_terminal" in result.redirect_url
    assert result.status == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_create_direct_payment_fails():
    """Test direct payment returns error (requires tokenized card)."""
    from app.services.payment.base import PaymentRequest
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test", use_redirect=False)
    request = PaymentRequest(order_id="order-123", amount=5000)

    result = await gateway.create_payment(request)

    assert result.success is False
    assert "tokenized" in result.error.lower()


# --- Confirmation Tests ---
@pytest.mark.asyncio
async def test_confirm_payment():
    """Test confirm_payment returns processing status."""
    from app.services.payment.base import PaymentStatus
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test")
    result = await gateway.confirm_payment("order-123")

    assert result.success is True
    assert result.status == PaymentStatus.PROCESSING


@pytest.mark.asyncio
async def test_get_payment_status():
    """Test get_payment_status returns pending."""
    from app.services.payment.base import PaymentStatus
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test")
    result = await gateway.get_payment_status("order-123")

    assert result.success is True
    assert result.status == PaymentStatus.PENDING


# --- Response Parsing Tests ---
def test_parse_response():
    """Test _parse_response parses Tranzila format."""
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test")
    response_text = "Response=000&ConfirmationCode=12345&orderId=order-123"

    result = gateway._parse_response(response_text)

    assert result["Response"] == "000"
    assert result["ConfirmationCode"] == "12345"
    assert result["orderId"] == "order-123"


# --- Callback Tests ---
def test_verify_callback_success():
    """Test verify_callback returns True for valid callback."""
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test")
    params = {"Response": "000", "ConfirmationCode": "12345"}

    assert gateway.verify_callback(params) is True


def test_verify_callback_failure():
    """Test verify_callback returns False for invalid callback."""
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test")
    params = {"Response": "001", "ConfirmationCode": ""}

    assert gateway.verify_callback(params) is False


def test_parse_callback_success():
    """Test parse_callback for successful payment."""
    from app.services.payment.base import PaymentStatus
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test")
    params = {"Response": "000", "ConfirmationCode": "12345", "orderId": "order-123"}

    result = gateway.parse_callback(params)

    assert result.success is True
    assert result.payment_id == "order-123"
    assert result.external_id == "12345"
    assert result.status == PaymentStatus.COMPLETED


def test_parse_callback_failure():
    """Test parse_callback for failed payment."""
    from app.services.payment.base import PaymentStatus
    from app.services.payment.tranzila import TranzilaGateway

    gateway = TranzilaGateway(terminal_name="test")
    params = {"Response": "001", "ConfirmationCode": "", "orderId": "order-123"}

    result = gateway.parse_callback(params)

    assert result.success is False
    assert result.status == PaymentStatus.FAILED
    assert "001" in result.error
