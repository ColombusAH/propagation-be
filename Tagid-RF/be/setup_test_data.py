#!/usr/bin/env python3
"""
Setup script to create initial business and test the database connection.
"""

import asyncio
from app.db.prisma import prisma_client

async def setup():
    """Create initial business for testing."""
    try:
        await prisma_client.connect()
        print("✅ Connected to database")
        
        # Check if business exists
        business = await prisma_client.client.business.find_first()
        
        if not business:
            print("Creating test business...")
            business = await prisma_client.client.business.create(
                data={
                    "name": "Test Business"
                }
            )
            print(f"✅ Created business: {business.id}")
        else:
            print(f"✅ Business exists: {business.id}")
        
        print(f"\nUse this business ID for testing: {business.id}")
        
        await prisma_client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup())
