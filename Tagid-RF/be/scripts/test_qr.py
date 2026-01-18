import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1"


async def test_qr_generation():
    sku = "TEST-WATCH-123"
    async with httpx.AsyncClient(timeout=10.0) as client:
        print(f"Testing QR Generation for SKU: {sku}")
        try:
            response = await client.get(f"{BASE_URL}/products/qr/{sku}")

            if response.status_code == 200:
                print("✅ QR Code generated successfully!")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print(f"Image Size: {len(response.content)} bytes")

                # Optional: Save to file to verify manually
                with open("test_qr.png", "wb") as f:
                    f.write(response.content)
                print("Saved to test_qr.png")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_qr_generation())
