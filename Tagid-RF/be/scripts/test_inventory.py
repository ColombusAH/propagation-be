import httpx
import asyncio
from pprint import pprint

BASE_URL = "http://localhost:8000/api/v1"

async def test_inventory_summary():
    async with httpx.AsyncClient(timeout=10.0) as client:
        print(f"Testing Inventory Summary: {BASE_URL}/inventory/summary")
        
        try:
            response = await client.get(f"{BASE_URL}/inventory/summary")
            response.raise_for_status()
            
            data = response.json()
            print("\n✅ Inventory Summary Received:")
            print(f"Total Products (SKUs): {data['total_products']}")
            print(f"Total Value (Cents): {data['total_value_cents']}")
            
            print("\n----- Details -----")
            for product in data['products']:
                print(f"📦 Product: {product['product_name']} (SKU: {product['product_sku']})")
                print(f"   Total: {product['total_items']}")
                print(f"   Available: {product['available_items']}")
                print(f"   Sold: {product['sold_items']}")
                print(f"   Price: {product['price_cents']}")
                print("-" * 20)
                
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_inventory_summary())
