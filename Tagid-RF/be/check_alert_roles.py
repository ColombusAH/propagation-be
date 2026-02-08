import asyncio
from app.db.prisma import prisma_client

async def check_roles():
    try:
        await prisma_client.connect()
        subs = await prisma_client.client.pushsubscription.find_many(include={"user": True})
        print(f"Total Subscriptions: {len(subs)}")
        for sub in subs:
            if sub.user:
                print(f"User: {sub.user.email} | Role: {sub.user.role} | ReceiveAlerts: {sub.user.receiveTheftAlerts}")
            else:
                print(f"Subscription {sub.id} has NO USER attached")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_roles())
