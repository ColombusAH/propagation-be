import asyncio
from app.db.prisma import prisma_client

async def fix_data():
    try:
        await prisma_client.connect()
        
        # 1. Get first user (Admin)
        user = await prisma_client.client.user.find_first()
        if not user:
            print("No user found! Cannot link subscription.")
            return

        print(f"Found User: {user.email} ({user.id})")

        # 2. Update user to allow alerts and be SUPER_ADMIN (just in case)
        await prisma_client.client.user.update(
            where={"id": user.id},
            data={
                "role": "SUPER_ADMIN",
                "receiveTheftAlerts": True
            }
        )
        print("Updated User to SUPER_ADMIN and receiveTheftAlerts=True")

        # 3. Link all subscriptions to this user
        result = await prisma_client.client.pushsubscription.update_many(
            where={},
            data={"userId": user.id}
        )
        print(f"Linked {result} subscriptions to user {user.email}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_data())
