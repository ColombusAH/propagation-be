import asyncio
import logging

from app.core.security import create_access_token, verify_access_token
from app.crud.user import get_user_by_email
from prisma import Prisma

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def debug_auth():
    db = Prisma()
    await db.connect()

    try:
        # 1. Check Businesses
        businesses = await db.business.find_many()
        print(f"\n--- Businesses ({len(businesses)}) ---")
        for b in businesses:
            print(f"ID: {b.id}, Name: {b.name}, Slug: {getattr(b, 'slug', 'N/A')}")

        # 2. Check Users
        users = await db.user.find_many()
        print(f"\n--- Users ({len(users)}) ---")
        for u in users:
            print(
                f"ID: {u.id}, Email: {u.email}, Role: {u.role}, BusinessId: {u.businessId}"
            )

        # 3. Simulate a Dev Login Token Generation
        if users:
            user = users[0]
            jwt_payload = {
                "sub": user.email,
                "user_id": user.id,
                "role": str(user.role),
                "business_id": user.businessId,
            }
            token = create_access_token(data=jwt_payload)
            print(f"\nGenerated Token for {user.email}: {token[:20]}...")

            # 4. Verify that same token
            verified_payload = verify_access_token(token)
            if verified_payload:
                print(f"SUCCESS: Token verified. Payload: {verified_payload}")
                if verified_payload.get("user_id") == user.id:
                    print("SUCCESS: user_id matches.")
                else:
                    print(
                        f"FAILURE: user_id mismatch! Payload has {verified_payload.get('user_id')}, expected {user.id}"
                    )
            else:
                print("FAILURE: Token verification failed!")
        else:
            print("\nNo users found to test token verification.")

    except Exception as e:
        logger.error(f"Debug auth failed: {e}", exc_info=True)
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(debug_auth())
