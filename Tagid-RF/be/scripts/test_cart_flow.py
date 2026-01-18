import asyncio
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api/v1"


async def test_cart_flow():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Add Item to Cart (Simulating QR Scan)
        # We need a valid SKU/EPC in the DB for this to work.
        # Assuming seed_inventory.py was run or we have some data.
        # Let's try to add a hypothetical item or rely on what's there.
        # For a robust test, we might need to create a tag first via API.

        logger.info("--- Step 1: Adding Item to Cart ---")

        # Create a test tag first to ensure availability
        epc = "E280689400000000TESTCART"
        sku = "TEST-CART-ITEM"

        # Create/Reset tag
        await client.post(
            f"{BASE_URL}/tags/",
            json={
                "epc": epc,
                "product_name": "Test Cart Item",
                "product_sku": sku,
                "price_cents": 5000,  # 50.00 ILS
                "is_paid": False,
            },
        )

        # Scan via Deep Link
        qr_data = f"tagid://product/{sku}"
        response = await client.post(f"{BASE_URL}/cart/add", json={"qr_data": qr_data})

        if response.status_code == 200:
            cart = response.json()
            logger.info(f"✅ Added to cart! Items: {len(cart['items'])}")
            logger.info(f"   Total: {cart['total_price_cents']/100} {cart['currency']}")
        else:
            logger.error(f"❌ Failed to add: {response.text}")
            return

        # 2. View Cart
        logger.info("\n--- Step 2: Viewing Cart ---")
        response = await client.get(f"{BASE_URL}/cart/")
        if response.status_code == 200:
            cart = response.json()
            logger.info(f"✅ Cart fetched. Items: {len(cart['items'])}")
        else:
            logger.error(f"❌ Failed to view cart: {response.text}")

        # 3. Checkout
        logger.info("\n--- Step 3: Checkout ---")
        response = await client.post(
            f"{BASE_URL}/cart/checkout",
            json={"payment_method_id": "pm_card_visa", "email": "customer@example.com"},  # Mock ID
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Checkout Successful!")
            logger.info(f"   Transaction ID: {result['transaction_id']}")
            logger.info(f"   Message: {result['message']}")
        else:
            logger.error(f"❌ Checkout Failed: {response.text}")

        # 4. Verify Start (Cart should be empty)
        logger.info("\n--- Step 4: Verify Empty Cart ---")
        response = await client.get(f"{BASE_URL}/cart/")
        cart = response.json()
        if cart["total_items"] == 0:
            logger.info("✅ Cart is empty.")
        else:
            logger.error(f"❌ Cart not empty! Items: {cart['total_items']}")


if __name__ == "__main__":
    asyncio.run(test_cart_flow())
