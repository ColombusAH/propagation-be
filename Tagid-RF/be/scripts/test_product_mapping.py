import asyncio
import sys

import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def test_product_mapping():
    print("🚀 Starting Tag -> Product Mapping Test...\n")

    async with httpx.AsyncClient() as client:
        # 1. Create a new tag (simulating a scan or import)
        epc = "TEST_EPC_MAPPING_001"
        print(f"1. Creating/Scanning tag with EPC: {epc}")

        # First, try to delete if exists to start clean
        try:
            # We don't have ID yet, so lookup by EPC first
            r = await client.get(f"{BASE_URL}/tags/epc/{epc}")
            if r.status_code == 200:
                tag_id = r.json()["id"]
                await client.delete(f"{BASE_URL}/tags/{tag_id}")
                print(f"   (Cleaned up existing tag with ID {tag_id})")
        except Exception:
            pass

        create_payload = {
            "epc": epc,
            "rssi": -50,
            "antenna_port": 1,
            "location": "Test Bench",
        }

        response = await client.post(f"{BASE_URL}/tags/", json=create_payload)
        if response.status_code != 201:
            print(f"❌ Failed to create tag: {response.text}")
            return

        tag_data = response.json()
        tag_id = tag_data["id"]
        print(f"✅ Tag created successfully! ID: {tag_id}")

        # 2. Update with Product Info (Mapping)
        print(f"\n2. Mapping Product Info to Tag {tag_id}...")
        update_payload = {
            "product_name": "Premium Wireless Mouse",
            "product_sku": "MS-WL-500",
            "price_cents": 4999,  # 49.99
            "store_id": 1,
            "is_paid": False,
        }

        response = await client.put(f"{BASE_URL}/tags/{tag_id}", json=update_payload)
        if response.status_code != 200:
            print(f"❌ Failed to update tag mapping: {response.text}")
            return

        updated_tag = response.json()

        # 3. Verify Persistence
        print(f"\n3. Verifying Persistence...")
        errors = []
        if updated_tag.get("product_name") != update_payload["product_name"]:
            errors.append(f"Product Name mismatch: {updated_tag.get('product_name')}")
        if updated_tag.get("product_sku") != update_payload["product_sku"]:
            errors.append(f"SKU mismatch: {updated_tag.get('product_sku')}")
        if updated_tag.get("price_cents") != update_payload["price_cents"]:
            errors.append(f"Price mismatch: {updated_tag.get('price_cents')}")

        if errors:
            print("❌ Verification Failed:")
            for e in errors:
                print(f"   - {e}")
        else:
            print("✅ Product mapping persisted correctly!")
            print(f"   Name: {updated_tag.get('product_name')}")
            print(f"   SKU: {updated_tag.get('product_sku')}")
            print(f"   Price: {updated_tag.get('price_cents')}")

        # 4. Simulate Scan Event (Ensure fields aren't wiped)
        print(f"\n4. Simulating new scan event for same tag...")
        scan_payload = {"epc": epc, "rssi": -45, "antenna_port": 1}  # Changed RSSI

        response = await client.post(f"{BASE_URL}/tags/", json=scan_payload)
        if (
            response.status_code == 201
        ):  # 201 is returned for both create and update in our API
            scanned_tag = response.json()
            if scanned_tag.get("product_name") == update_payload["product_name"]:
                print("✅ Product info preserved after re-scan!")
            else:
                print(
                    f"❌ WARNING: Product info lost after re-scan! Got: {scanned_tag.get('product_name')}"
                )
        else:
            print(f"❌ Failed to process scan: {response.text}")

    print("\n🏁 Test Completed.")


if __name__ == "__main__":
    try:
        asyncio.run(test_product_mapping())
    except Exception as e:
        print(f"❌ Error running test (is the server running?): {str(e)}")
