#!/usr/bin/env python
"""
Simple database connection checker for troubleshooting.
"""
import os
import sys
import asyncio
import socket
from urllib.parse import urlparse

try:
    from prisma import Prisma
    PRISMA_AVAILABLE = True
except ImportError:
    PRISMA_AVAILABLE = False
    print("Warning: Prisma package not available")

async def main():
    print("=== Database Connection Check ===")
    
    # Get DATABASE_URL
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable not set")
        return False
    
    # Parse connection info
    parsed = urlparse(db_url)
    host = parsed.hostname
    port = parsed.port or 5432
    database = parsed.path.lstrip('/')
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    
    # Check hostname resolution
    try:
        ip_address = socket.gethostbyname(host)
        print(f"✓ Hostname resolves to IP: {ip_address}")
    except socket.gaierror:
        print(f"✗ Failed to resolve hostname: '{host}'")
        return False
    
    # Check port connectivity
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.close()
        print(f"✓ Successfully connected to {host}:{port}")
    except (socket.timeout, socket.error) as e:
        print(f"✗ Failed to connect to {host}:{port}: {e}")
        return False
    
    # Check Prisma connection
    if PRISMA_AVAILABLE:
        try:
            print("Connecting via Prisma...")
            prisma = Prisma()
            await prisma.connect()
            result = await prisma.query_raw("SELECT 1 as test")
            await prisma.disconnect()
            print(f"✓ Prisma query successful: {result}")
        except Exception as e:
            print(f"✗ Prisma error: {e}")
            return False
    
    print("✓ All connection checks passed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 