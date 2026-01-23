import asyncio

import httpx

from app.main import app


async def test_dev_login():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        try:
            print("Calling /api/v1/auth/dev-login...")
            response = await client.post("/api/v1/auth/dev-login", json={"role": "STORE_MANAGER"})
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_dev_login())
