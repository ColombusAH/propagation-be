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
from httpx import AsyncClient
from app.core.config import settings
from app.db.prisma import prisma_client


@pytest.mark.asyncio
async def test_full_rfid_flow(
    async_client: AsyncClient, normal_user_token_headers: dict, db_session
):
    """End‑to‑end test of the RFID core flow.
    Steps:
    1. Create Business and Store.
    2. Add an RFID Reader (type GATE).
    3. Create a Product tag (RfidTag) linked to a product SKU.
    4. Simulate a scan via the Cart QR endpoint.
    5. Verify the tag appears in the cart.
    6. Trigger a "Bath" sync with multiple EPCs.
    7. Ensure an inventory snapshot is recorded.
    8. If the tag is unpaid, verify a theft alert is generated.
    """
    # 1. Business & Store creation
    async with prisma_client.client as db:
        business = await db.business.create(data={"name": "TestBiz", "slug": "testbiz"})
        store = await db.store.create(
            data={"name": "Main Store", "businessId": business.id, "slug": "mainstore"}
        )

        # 2. Reader creation (GATE type)
        reader = await db.rfidreader.create(
            data={
                "name": "GateReader1",
                "ipAddress": "192.168.1.100",
                "type": "GATE",
                "storeId": store.id,
            }
        )

        # 3. Product tag creation
        tag = await db.rfidtag.create(
            data={
                "epc": "EPC1234567890",
                "productId": "SKU-001",
                "productDescription": "Test Product",
                "isPaid": False,
                "status": "ACTIVE",
            }
        )

    # 4. Simulate QR scan (add to cart)
    add_response = await async_client.post(
        f"{settings.API_V1_STR}/cart/add",
        json={"qr_data": f"tagid://product/{tag.productId}"},
        headers=normal_user_token_headers,
    )
    assert add_response.status_code == 200
    cart_data = add_response.json()
    assert any(item["epc"] == tag.epc for item in cart_data["items"])

    # 5. Bath sync with a list of EPCs (including the same tag)
    bath_response = await async_client.post(
        f"{settings.API_V1_STR}/cart/sync-bath",
        json=[tag.epc],
        headers=normal_user_token_headers,
    )
    assert bath_response.status_code == 200
    bath_data = bath_response.json()
    assert len(bath_data["items"]) == 1

    # 6. Verify inventory snapshot was created (using service directly)
    async with prisma_client.client as db:
        snapshot = await db.inventorysnapshot.find_first(
            where={"readerId": reader.id}, order={"timestamp": "desc"}
        )
        assert snapshot is not None
        assert snapshot.itemCount >= 1

    # 7. Verify theft alert (should exist for unpaid tag scanned at GATE)
    async with prisma_client.client as db:
        alert = await db.theftalert.find_first(where={"tagId": tag.id})
        assert alert is not None
        assert alert.resolved is False

    # Cleanup – delete created records (optional, depending on test DB handling)
    # This is left as an exercise for the test environment.
