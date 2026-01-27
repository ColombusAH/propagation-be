import asyncio
import httpx

async def test_payment_flow():
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
        print(f"✅ Login SUCCESS! Got token: {token[:50]}...")
        
        # Step 2: Create Payment Intent
        print("\nStep 2: Creating payment intent...")
        headers = {"Authorization": f"Bearer {token}"}
        payment_response = await client.post(
            f"{base_url}/payment/create-intent",
            json={
                "order_id": "TEST_ORDER_123",
                "amount": 500,
                "currency": "ILS",
                "payment_provider": "STRIPE",
                "metadata": {}
            },
            headers=headers
        )
        
        if payment_response.status_code != 200:
            print(f"❌ Payment Intent FAILED: {payment_response.status_code}")
            print(payment_response.text)
            return
        
        payment_data = payment_response.json()
        print(f"✅ Payment Intent SUCCESS!")
        print(f"   Payment ID: {payment_data.get('payment_id')}")
        print(f"   External ID: {payment_data.get('external_id')}")
        print(f"   Client Secret: {payment_data.get('client_secret', 'N/A')[:30]}...")
        print(f"   Status: {payment_data.get('status')}")
        
        print("\n🎉 ALL TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_payment_flow())
