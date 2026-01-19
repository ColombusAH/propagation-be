import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_reader():
    print("\n" + "=" * 50)
    print("RFID HARDWARE DEBUG TOOL")
    print("=" * 50 + "\n")

    try:
        from app.services.rfid_reader import rfid_reader_service

        # Override IP if provided in args
        if len(sys.argv) > 1:
            rfid_reader_service.reader_ip = sys.argv[1]
            print(f"⚠️  Overriding Target IP to: {rfid_reader_service.reader_ip}")

        # Try to connect to specified port first
        print(f"Target Reader IP: {rfid_reader_service.reader_ip}")
        print(f"Target Reader Port: {rfid_reader_service.reader_port}")

        # Test basic reachable first
        import socket

        async def check_port(ip, port):
            try:
                print(f"  Checking {ip}:{port}...", end="", flush=True)
                fut = asyncio.open_connection(ip, port)
                reader, writer = await asyncio.wait_for(fut, timeout=2.0)
                writer.close()
                await writer.wait_closed()
                print(" OPEN! ✅")
                return True
            except Exception:
                print(" closed/timeout ❌")
                return False

        # Attempt connection to configured port
        print("\nChecking configured port...")
        if await check_port(
            rfid_reader_service.reader_ip, rfid_reader_service.reader_port
        ):
            print("Port is open, establishing service connection...")
            connected = await rfid_reader_service.connect()
        else:
            connected = False
            print("\nConfigured port failed. Scanning common RFID ports...")
            common_ports = [4001, 6000, 27011, 2022, 5000, 80, 8080]
            if rfid_reader_service.reader_port in common_ports:
                common_ports.remove(rfid_reader_service.reader_port)

            for port in common_ports:
                if await check_port(rfid_reader_service.reader_ip, port):
                    print(f"\n🎉 FOUND OPEN PORT: {port}")
                    print(f"Updating service to use port {port}...")
                    rfid_reader_service.reader_port = port
                    connected = await rfid_reader_service.connect()
                    if connected:
                        break

        if connected:
            print("\n✅ CONNECTION SUCCESSFUL!")

            # Get info
            info = await rfid_reader_service.get_reader_info()
            print(f"Reader Info: {info}")

            print("\nAttempting single tag read...")
            tags = await rfid_reader_service.read_single_tag()

            if tags:
                print(f"✅ READ {len(tags)} TAGS:")
                for tag in tags:
                    print(
                        f"  - EPC: {tag.get('epc')}, RSSI: {tag.get('rssi')}, ANT: {tag.get('antenna_port')}"
                    )
            else:
                print("⚠️  No tags detected in single read cycle.")

            print("\nDisconnecting...")
            await rfid_reader_service.disconnect()
            print("Disconnected.")

        else:
            print("\n❌ CONNECTION FAILED.")
            print(
                "Please check:\n1. Reader is powered on\n2. Ethernet cable is connected\n3. IP address matches settings (env var RFID_READER_IP)"
            )

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you are running this from the backend root directory (be/)")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_reader())
