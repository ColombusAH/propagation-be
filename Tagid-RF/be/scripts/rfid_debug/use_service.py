#!/usr/bin/env python3
"""
Use the actual rfid_reader_service that worked before.
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

# Set environment variables
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
os.environ.setdefault("SECRET_KEY", "test_secret_key")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test_google_client_id")
os.environ.setdefault("RFID_DATABASE_URL", "postgresql://test:test@localhost:5432/test_rfid_db")
os.environ.setdefault("RFID_READER_IP", "192.168.1.200")
os.environ.setdefault("RFID_READER_PORT", "2022")


async def main():
    print("=" * 70)
    print("Using rfid_reader_service")
    print("=" * 70)
    
    from app.services.rfid_reader import rfid_reader_service
    
    # Override IP/port
    rfid_reader_service.reader_ip = "192.168.1.200"
    rfid_reader_service.reader_port = 2022
    
    print(f"\nConnecting to {rfid_reader_service.reader_ip}:{rfid_reader_service.reader_port}...")
    
    connected = await rfid_reader_service.connect()
    
    if connected:
        print("✓ Connected!")
        
        print("\nGetting reader info...")
        info = await rfid_reader_service.get_reader_info()
        print(f"Reader Info: {info}")
        
        print("\nReading tags (single shot)...")
        tags = await rfid_reader_service.read_single_tag()
        
        if tags:
            print(f"\n✓ Found {len(tags)} tag(s):")
            for tag in tags:
                print(f"  - EPC: {tag.get('epc')}")
                print(f"    RSSI: {tag.get('rssi')} dBm")
                print(f"    Antenna: {tag.get('antenna_port')}")
        else:
            print("No tags found")
        
        print("\nDisconnecting...")
        await rfid_reader_service.disconnect()
        print("Done.")
    else:
        print("❌ Connection failed")


if __name__ == "__main__":
    asyncio.run(main())
