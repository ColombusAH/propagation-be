#!/usr/bin/env python3
"""
Direct test of user creation to see the actual error.
"""

import asyncio

from app.crud.user import create_user
from app.db.prisma import prisma_client


async def test_create():
    """Test creating a user directly."""
    try:
        await prisma_client.connect()
        print("✅ Connected to database")

        user = await create_user(
            db=prisma_client.client,
            email="directtest@test.com",
            password="password123",
            name="Direct Test",
            phone="1234567890",
            address="123 Test St",
            business_id="dc33f1dc-7fca-4628-bd75-e8b6eb6d8ca6",
            role="CUSTOMER",
        )

        print(f"✅ User created: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")

        await prisma_client.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_create())
