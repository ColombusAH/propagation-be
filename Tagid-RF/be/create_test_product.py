import asyncio
from app.db.prisma import prisma_client

async def create_test_product():
    await prisma_client.connect()
    
    # Create multiple products
    test_products = [
        {"name": "חלה טרייה לשבת", "price": 12.0, "sku": "bread-12", "desc": "מאפייה מקומית"},
        {"name": "חלב תנובה 3%", "price": 6.30, "sku": "milk-6", "desc": "מוצרי חלב"},
        {"name": "קפה נמס עלית", "price": 24.90, "sku": "coffee-24", "desc": "משקאות חמים"},
        {"name": "מוצר בדיקה 5 שקלים", "price": 5.0, "sku": "test-prod-5", "desc": "מוצר לבדיקת תשלום"}
    ]
    
    for p_data in test_products:
        # Check if exists
        existing = await prisma_client.client.product.find_first(where={"sku": p_data["sku"]})
        if not existing:
            product = await prisma_client.client.product.create(
                data={
                    "name": p_data["name"],
                    "price": p_data["price"],
                    "sku": p_data["sku"],
                    "storeId": store.id,
                    "description": p_data["desc"]
                }
            )
            print(f"✅ Created product: {product.name} (ID: {product.id})")
            
            # Create tag
            epc = f"E2000000000000000{p_data['sku'].split('-')[-1].zfill(7)}"
            await prisma_client.client.rfidtag.create(
                data={
                    "epc": epc,
                    "productId": product.id,
                    "productDescription": product.name,
                    "status": "REGISTERED"
                }
            )
            print(f"✅ Created tag: {epc}")
        else:
            print(f"ℹ️ Product already exists: {p_data['name']}")
    
    await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(create_test_product())
