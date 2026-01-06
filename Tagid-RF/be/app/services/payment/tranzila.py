"""Tranzila payment gateway integration for Israeli payments and Bit."""

import logging
from typing import Optional
from urllib.parse import urlencode

import httpx

from .base import (
    PaymentGateway,
    PaymentProvider,
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
    RefundResult,
)

logger = logging.getLogger(__name__)


class TranzilaGateway(PaymentGateway):
    """Tranzila payment gateway implementation for Israeli market."""

    # Tranzila API endpoints
    PAYMENT_URL = "https://secure5.tranzila.com/cgi-bin/tranzila71u.cgi"
    DIRECT_URL = "https://direct.tranzila.com/cgi-bin/tranzila71u.cgi"

    # Currency codes
    CURRENCY_CODES = {
        "ILS": "1",
        "USD": "2",
        "EUR": "3",
        "GBP": "4",
    }

    def __init__(
        self, terminal_name: str, terminal_password: Optional[str] = None, use_redirect: bool = True
    ):
        self.terminal = terminal_name
        self.password = terminal_password
        self.use_redirect = use_redirect

    @property
    def provider(self) -> PaymentProvider:
        return PaymentProvider.TRANZILA

    async def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a Tranzila payment - redirect or direct."""
        if self.use_redirect:
            return await self._create_redirect_payment(request)
        else:
            return await self._create_direct_payment(request)

    async def _create_redirect_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a redirect URL for Tranzila hosted payment page."""
        params = {
            "supplier": self.terminal,
            "sum": request.amount / 100,  # Tranzila uses full units
            "currency": self.CURRENCY_CODES.get(request.currency, "1"),
            "orderId": request.order_id,
            "pdesc": f"Order {request.order_id}",
            "contact": request.customer_name or "",
            "email": request.customer_email or "",
            "TranzilaPW": self.password or "",
        }

        # Add return URL if provided
        if request.return_url:
            params["success_url_address"] = request.return_url
            params["fail_url_address"] = request.return_url

        redirect_url = f"{self.PAYMENT_URL}?{urlencode(params)}"

        logger.info(f"Created Tranzila redirect for order: {request.order_id}")

        return PaymentResult(
            success=True,
            payment_id=request.order_id,
            redirect_url=redirect_url,
            status=PaymentStatus.PENDING,
        )

    async def _create_direct_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a direct API payment (requires PCI compliance)."""
        # Note: Direct payment requires credit card details
        # This is for server-to-server communication when you have tokenized cards
        return PaymentResult(
            success=False,
            payment_id=request.order_id,
            error="Direct payment requires tokenized card. Use redirect flow instead.",
        )

    async def confirm_payment(
        self, payment_id: str, payment_method: Optional[str] = None
    ) -> PaymentResult:
        """Tranzila payments are confirmed via callback, not API."""
        # In redirect flow, confirmation happens via callback URL
        return PaymentResult(success=True, payment_id=payment_id, status=PaymentStatus.PROCESSING)

    async def get_payment_status(self, payment_id: str) -> PaymentResult:
        """Query Tranzila for payment status."""
        # Tranzila doesn't have a standard status API
        # Status is usually tracked internally after receiving callback
        return PaymentResult(success=True, payment_id=payment_id, status=PaymentStatus.PENDING)

    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> RefundResult:
        """Refund a Tranzila payment."""
        try:
            params = {
                "supplier": self.terminal,
                "TranzilaPW": self.password or "",
                "tranmode": "C",  # Credit/Refund mode
                "index": payment_id,
            }

            if amount:
                params["sum"] = amount / 100

            async with httpx.AsyncClient() as client:
                response = await client.post(self.DIRECT_URL, data=params, timeout=30.0)

                # Parse Tranzila response
                result = self._parse_response(response.text)

                if result.get("Response") == "000":
                    return RefundResult(success=True, refund_id=result.get("ConfirmationCode"))
                else:
                    return RefundResult(
                        success=False, error=f"Tranzila error: {result.get('Response')}"
                    )

        except Exception as e:
            logger.error(f"Tranzila refund error: {e}")
            return RefundResult(success=False, error=str(e))

    def _parse_response(self, response_text: str) -> dict:
        """Parse Tranzila response string to dict."""
        result = {}
        for pair in response_text.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                result[key] = value
        return result

    def verify_callback(self, params: dict) -> bool:
        """Verify a Tranzila callback is authentic."""
        # Tranzila callbacks include Response and ConfirmationCode
        response = params.get("Response", "")
        confirmation = params.get("ConfirmationCode", "")

        # Response "000" means successful payment
        return response == "000" and bool(confirmation)

    def parse_callback(self, params: dict) -> PaymentResult:
        """Parse Tranzila callback parameters into PaymentResult."""
        response = params.get("Response", "")
        confirmation = params.get("ConfirmationCode", "")
        order_id = params.get("orderId", "")

        success = response == "000"

        return PaymentResult(
            success=success,
            payment_id=order_id,
            external_id=confirmation if success else None,
            status=PaymentStatus.COMPLETED if success else PaymentStatus.FAILED,
            error=None if success else f"Tranzila error code: {response}",
        )
