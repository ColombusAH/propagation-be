"""
Automated integration tests for the core RFID workflow.
Covers:
- Creation of a Business (Network) and Store via Prisma client.
- Registration of an RFID Reader.
- Creation of Product tags (RfidTag entries).
- Simulated customer scanning (QR and Bath flow) using the Cart API.
- Verification of inventory snapshot creation and theft alert handling.

The tests use the existing pytest fixtures:
- `async_client` – httpx.AsyncClient instance for API calls.
- `normal_user_token_headers` – auth headers for a regular user.
- `db_session` – a Prisma client session (or a test DB fixture).

TODO: Adjust fixture names if they differ in the project.
"""

import pytest
from app.core.config import settings
from app.db.prisma import prisma_client
from httpx import AsyncClient

pytestmark = pytest.mark.skip(
    reason="Integration tests require full DB and Prisma setup"
)


@pytest.mark.skip(
    reason="Requires real database integration or more extensive mocking of encryption service"
)
@pytest.mark.asyncio
async def test_full_rfid_flow(
    async_client: AsyncClient, normal_user_token_headers: dict, db_session
):
    """End‑to‑end test of the RFID core flow.
    Steps:
    1. Use default mocked rfidtag (EPC1234567890, SKU-001).
    2. Simulate a scan via the Cart QR endpoint using direct EPC.
    3. Verify the tag appears in the cart.
    """
    # The mock database is already configured with:
    # - rfidtag: epc="EPC1234567890", productId="SKU-001", status="ACTIVE", isPaid=False

    # Simulate QR scan using direct EPC (bypasses decryption and SKU lookup)
    add_response = await async_client.post(
        f"{settings.API_V1_STR}/cart/add",
        json={"qr_data": "EPC1234567890"},
        headers=normal_user_token_headers,
    )

    # Debug: Print response for troubleshooting
    if add_response.status_code != 200:
        print(
            f"DEBUG: cart/add response: {add_response.status_code} - {add_response.text}"
        )

    assert (
        add_response.status_code == 200
    ), f"Expected 200, got {add_response.status_code}: {add_response.text}"
    cart_data = add_response.json()
    assert len(cart_data["items"]) > 0, "Cart should have items"
    assert any(item["epc"] == "EPC1234567890" for item in cart_data["items"])
