
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    try:
        await db.connect()
        user = await db.user.update(
            where={'email': 'eliran8hadad@gmail.com'},
            data={'isVerified': True, 'verificationCode': None}
        )
        print(f"User {user.email} is now VERIFIED.")
        await db.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
