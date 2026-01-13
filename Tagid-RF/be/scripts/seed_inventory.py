import sys
import os
import random
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database import SessionLocal
from app.models.rfid_tag import RFIDTag

def seed_inventory():
    db = SessionLocal()
    try:
        print("Seeding Inventory Data...")
        
        # Clear existing
        db.query(RFIDTag).delete()
        
        products = [
            # 3 Smart Watches: 2 Paid, 1 Unpaid (Available)
            {
                "epc": "E28011112222333344445555",
                "product_name": "Galaxy Watch 6",
                "product_sku": "GW6-BLK",
                "price_cents": 29900,
                "is_paid": True,
                "store_id": 1
            },
            {
                "epc": "E28011112222333344446666",
                "product_name": "Galaxy Watch 6",
                "product_sku": "GW6-BLK",
                "price_cents": 29900,
                "is_paid": True,
                "store_id": 1
            },
            {
                "epc": "E28011112222333344447777",
                "product_name": "Galaxy Watch 6",
                "product_sku": "GW6-BLK",
                "price_cents": 29900,
                "is_paid": False, # AVAILABLE
                "store_id": 1
            },
            
            # 2 Headphones: 0 Paid, 2 Unpaid (Available)
            {
                "epc": "E280AAAABBBBCCCCDDDDEEEE",
                "product_name": "Sony WH-1000XM5",
                "product_sku": "SONY-XM5",
                "price_cents": 34900,
                "is_paid": False, # AVAILABLE
                "store_id": 1
            },
            {
                "epc": "E280AAAABBBBCCCCDDDDIFFF",
                "product_name": "Sony WH-1000XM5",
                "product_sku": "SONY-XM5",
                "price_cents": 34900,
                "is_paid": False, # AVAILABLE
                "store_id": 1
            }
        ]
        
        for p in products:
            tag = RFIDTag(
                epc=p["epc"],
                product_name=p["product_name"],
                product_sku=p["product_sku"],
                price_cents=p["price_cents"],
                is_paid=p["is_paid"],
                store_id=p["store_id"],
                last_seen=datetime.now()
            )
            db.add(tag)
        
        db.commit()
        print(f"✅ Seeded {len(products)} tags.")
        
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_inventory()
