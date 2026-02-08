import asyncio
from app.db.prisma import prisma_client
from app.core.security import get_password_hash
from prisma.enums import Role

async def create_admin():
    try:
        await prisma_client.connect()
        
        # 1. Get or Create Business
        business = await prisma_client.client.business.find_first()
        if not business:
            print("Creating default business...")
            business = await prisma_client.client.business.create(
                data={
                    "name": "Default Business",
                    "slug": "default-biz"
                }
            )
        print(f"Business: {business.id}")

        # 2. Get or Create Admin User
        email = "admin@example.com"
        user = await prisma_client.client.user.find_unique(where={"email": email})
        
        if not user:
            print(f"Creating user {email}...")
            user = await prisma_client.client.user.create(
                data={
                    "email": email,
                    "hashedPassword": get_password_hash("admin123"),
                    "name": "Admin User",
                    "phone": "0500000000",
                    "address": "Admin Address",
                    "role": Role.SUPER_ADMIN,
                    "receiveTheftAlerts": True,
                    "businessId": business.id
                }
            )
        else:
            print(f"User {email} exists. Updating perms...")
            await prisma_client.client.user.update(
                where={"id": user.id},
                data={
                    "role": Role.SUPER_ADMIN,
                    "receiveTheftAlerts": True,
                    "businessId": business.id 
                }
            )

        print(f"User ID: {user.id}")

        # 3. Link subscriptions
        result = await prisma_client.client.pushsubscription.update_many(
            where={},
            data={"userId": user.id}
        )
        print(f"Linked {result} subscriptions to {email}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(create_admin())
