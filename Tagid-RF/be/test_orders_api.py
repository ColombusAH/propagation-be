import asyncio
import httpx

async def test_orders_api():
    base_url = "http://localhost:8000/api/v1"
    
    # Step 1: Login to get a token
    print("Step 1: Logging in as CUSTOMER...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{base_url}/auth/dev-login",
            json={"role": "CUSTOMER"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login FAILED: {login_response.status_code}")
            print(login_response.text)
            return
        
        login_data = login_response.json()
        token = login_data.get("token")
        print(f"✅ Login SUCCESS!")
        
        # Step 2: Fetch Orders
        print("\nStep 2: Fetching order history...")
        headers = {"Authorization": f"Bearer {token}"}
        orders_response = await client.get(
            f"{base_url}/orders/",
            headers=headers
        )
        
        if orders_response.status_code != 200:
            print(f"❌ Orders Fetch FAILED: {orders_response.status_code}")
            print(orders_response.text)
            return
        
        orders_data = orders_response.json()
        print(f"✅ Orders Fetch SUCCESS!")
        print(f"   Total Orders: {orders_data.get('total', 0)}")
        
        for order in orders_data.get('orders', [])[:5]:  # Show first 5
            print(f"   - #{order['id'][:8]}: {order['totalInCents']/100:.2f} {order['currency']} ({order['status']})")
        
        print("\n🎉 ORDERS API TEST PASSED!")

if __name__ == "__main__":
    asyncio.run(test_orders_api())
