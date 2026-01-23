#!/usr/bin/env python3
"""
Quick test script for M-200 RFID reader connection.

Usage:
    python test_m200.py
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.m200_protocol import M200Command, M200Commands
from app.services.rfid_reader import rfid_reader_service


async def test_connection():
    """Test M-200 connection and basic operations."""

    print("=" * 60)
    print("M-200 RFID Reader Test")
    print("=" * 60)

    # Test 1: Connection
    print("\n[1/4] Testing connection...")
    success = await rfid_reader_service.connect()

    if not success:
        print("❌ Connection failed!")
        print("\nTroubleshooting:")
        print("  1. Check M-200 IP address in .env")
        print("  2. Verify network connectivity: ping <M200_IP>")
        print("  3. Check port accessibility: telnet <M200_IP> 4001")
        print("  4. Ensure M-200 TCP server is enabled")
        return False

    print("✅ Connected successfully!")

    # Test 2: Device Info
    print("\n[2/4] Getting device information...")
    info = await rfid_reader_service.get_reader_info()

    if info.get("connected"):
        print("✅ Device info retrieved:")
        print(f"   Model: {info.get('model', 'Unknown')}")
        print(f"   Type: {info.get('reader_type', 'Unknown')}")
        print(f"   Serial: {info.get('serial_number', 'Unknown')}")
        print(f"   RFID FW: {info.get('rfid_firmware_version', 'Unknown')}")
        print(f"   CP FW: {info.get('cp_firmware_version', 'Unknown')}")
    else:
        print(f"⚠️  Could not get device info: {info.get('error', 'Unknown error')}")

    # Test 3: Single Tag Read
    print("\n[3/4] Testing single tag read...")
    print("   Place a tag near the M-200 reader...")

    tags = await rfid_reader_service.read_single_tag()

    if tags:
        print(f"✅ Found {len(tags)} tag(s):")
        for i, tag in enumerate(tags, 1):
            print(f"   Tag {i}:")
            print(f"     EPC: {tag.get('epc')}")
            print(f"     RSSI: {tag.get('rssi')} dBm")
            print(f"     Antenna: {tag.get('antenna_port')}")
            print(f"     PC: 0x{tag.get('pc', 0):04X}")
    else:
        print("⚠️  No tags detected")
        print("   Make sure a tag is within range (0-10m)")

    # Test 4: Disconnect
    print("\n[4/4] Disconnecting...")
    await rfid_reader_service.disconnect()
    print("✅ Disconnected")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

    return True


async def test_continuous_scan(duration: int = 10):
    """Test continuous scanning for specified duration."""

    print("\n" + "=" * 60)
    print(f"Continuous Scan Test ({duration} seconds)")
    print("=" * 60)

    # Connect
    print("\nConnecting...")
    success = await rfid_reader_service.connect()
    if not success:
        print("❌ Connection failed!")
        return

    print("✅ Connected")

    # Start scanning
    print(f"\nStarting scan for {duration} seconds...")
    print("Place tags near the reader...\n")

    tag_count = 0

    def tag_callback(tag_data):
        nonlocal tag_count
        tag_count += 1
        print(
            f"  [{tag_count}] EPC: {tag_data.get('epc')}, RSSI: {tag_data.get('rssi')} dBm"
        )

    await rfid_reader_service.start_scanning(callback=tag_callback)

    # Wait
    await asyncio.sleep(duration)

    # Stop
    print("\nStopping scan...")
    await rfid_reader_service.stop_scanning()

    print(f"\n✅ Scan complete! Total tags read: {tag_count}")

    # Disconnect
    await rfid_reader_service.disconnect()
    print("✅ Disconnected")


def main():
    """Main test function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test M-200 RFID reader")
    parser.add_argument(
        "--scan", type=int, metavar="SECONDS", help="Run continuous scan for N seconds"
    )

    args = parser.parse_args()

    try:
        if args.scan:
            asyncio.run(test_continuous_scan(args.scan))
        else:
            asyncio.run(test_connection())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
