#!/usr/bin/env python3
"""
Direct SQL migration to update Role enum.
"""

import asyncio
import os
from prisma import Prisma


async def migrate_roles():
    """Update Role enum in database."""

    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/shifty")

    print(f"Connecting to database...")

    # Create Prisma client
    db = Prisma()
    await db.connect()

    try:
        print("Updating Role enum...")

        # SQL to update the enum
        sql_commands = [
            # Add new enum values
            "ALTER TYPE \"Role\" ADD VALUE IF NOT EXISTS 'SUPER_ADMIN';",
            "ALTER TYPE \"Role\" ADD VALUE IF NOT EXISTS 'NETWORK_MANAGER';",
            "ALTER TYPE \"Role\" ADD VALUE IF NOT EXISTS 'STORE_MANAGER';",
            "ALTER TYPE \"Role\" ADD VALUE IF NOT EXISTS 'CUSTOMER';",
        ]

        for sql in sql_commands:
            print(f"Executing: {sql}")
            await db.execute_raw(sql)
            print("✅ Success")

        print("\n✅ Migration complete!")
        print("\nAvailable roles:")
        print("- SUPER_ADMIN")
        print("- NETWORK_MANAGER")
        print("- STORE_MANAGER")
        print("- EMPLOYEE")
        print("- CUSTOMER")
        print("- OWNER (legacy)")
        print("- ADMIN (legacy)")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(migrate_roles())
