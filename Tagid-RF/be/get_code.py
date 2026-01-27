
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    try:
        await db.connect()
        user = await db.user.find_unique(where={'email': 'eliran8hadad@gmail.com'})
        if user:
            print(f"User: {user.email}")
            print(f"Verification Code: {user.verificationCode}")
            print(f"Is Verified: {user.isVerified}")
        else:
            print("User not found")
        await db.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
