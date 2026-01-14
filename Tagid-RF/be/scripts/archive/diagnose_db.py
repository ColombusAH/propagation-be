
import os
import sys
import asyncio
import socket

# Try to import prisma to check availability
try:
    from prisma import Prisma
    PRISMA_AVAILABLE = True
except ImportError:
    PRISMA_AVAILABLE = False

async def test_socket_connection(host, port):
    print(f"Testing TCP connection to {host}:{port}...")
    try:
        reader, writer = await asyncio.open_connection(host, port)
        print("  [SUCCESS] TCP Connection established.")
        writer.close()
        await writer.wait_closed()
        return True
    except Exception as e:
        print(f"  [FAILURE] TCP Connection failed: {e}")
        return False

async def main():
    print("=== RFID Simulation Diagnostic Tool ===")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Check Environment Variables
    db_url = os.environ.get("DATABASE_URL")
    print(f"DATABASE_URL Env: {db_url}")
    
    if not db_url:
        print("WARNING: DATABASE_URL not found in environment variables.")
        # Try to read .env manually
        if os.path.exists(".env"):
            print("Found .env file. Reading...")
            with open(".env", "r") as f:
                for line in f:
                    if line.strip().startswith("DATABASE_URL="):
                        print(f"File .env DATABASE_URL: {line.strip()}")
        else:
            print(".env file NOT found.")
    
    # Parse DB URL for host/port (Naive parsing)
    host = "127.0.0.1"
    port = 5432
    if db_url and "@" in db_url:
        try:
            # postgresql://user:pass@host:port/db
            part = db_url.split("@")[1]
            host_port = part.split("/")[0]
            if ":" in host_port:
                host, port = host_port.split(":")
                port = int(port)
            else:
                host = host_port
        except Exception:
            pass
            
    # Test Connectivity
    await test_socket_connection(host, port)
    
    # Test Prisma Connection
    if PRISMA_AVAILABLE:
        print("\nAttempting Prisma Connection...")
        prisma = Prisma()
        try:
            await prisma.connect()
            print("  [SUCCESS] Prisma connected successfully!")
            await prisma.disconnect()
        except Exception as e:
            print(f"  [FAILURE] Prisma connection failed: {e}")
            from prisma.engine.errors import EngineConnectionError
            if isinstance(e, EngineConnectionError):
                 print(f"  Detail: {e}")

    else:
        print("\nPrisma client not installed in this environment.")

if __name__ == "__main__":
    asyncio.run(main())
