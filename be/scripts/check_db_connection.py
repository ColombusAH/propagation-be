#!/usr/bin/env python
"""
Database connection checker for troubleshooting.
"""
import os
import sys
import asyncio
import socket
import time
from urllib.parse import urlparse
import subprocess

# Try to import Prisma
try:
    from prisma import Prisma
    from prisma.errors import PrismaError
    PRISMA_AVAILABLE = True
except ImportError:
    PRISMA_AVAILABLE = False
    print("Warning: Prisma package not available. Some tests will be skipped.")


def get_db_connection_info():
    """Parse database connection info from DATABASE_URL"""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Mask password in output
    print(f"Using DATABASE_URL: {db_url.replace('://', '://***:***@').split('@', 1)[1]}")
    
    # Parse URL
    parsed = urlparse(db_url)
    
    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip('/'),
        "full_url": db_url
    }


def check_hostname_resolution(host):
    """Check if the hostname can be resolved"""
    print(f"\n== Checking hostname resolution for '{host}' ==")
    try:
        ip_address = socket.gethostbyname(host)
        print(f"✓ Hostname '{host}' resolves to IP: {ip_address}")
        return True
    except socket.gaierror:
        print(f"✗ Failed to resolve hostname: '{host}'")
        print("  → Check your network configuration and DNS settings")
        return False


def check_port_connectivity(host, port):
    """Check if we can connect to the specified port"""
    print(f"\n== Checking port connectivity to {host}:{port} ==")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.close()
        print(f"✓ Successfully connected to {host}:{port}")
        return True
    except (socket.timeout, socket.error) as e:
        print(f"✗ Failed to connect to {host}:{port}: {e}")
        print("  → Check if database is running and firewall settings")
        return False


def run_network_diagnostics(host):
    """Run basic network diagnostics"""
    print("\n== Running network diagnostics ==")
    
    # Try ping
    try:
        result = subprocess.run(
            ["ping", "-c", "3", host], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        print(f"Ping results for {host}:")
        print(result.stdout)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Ping command failed: {e}")
    
    # Try traceroute if available
    try:
        result = subprocess.run(
            ["traceroute", "-m", "5", host], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        print(f"Traceroute results for {host}:")
        print(result.stdout)
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Traceroute command failed: {e}")


async def check_prisma_connection(db_info):
    """Check if Prisma can connect to the database"""
    if not PRISMA_AVAILABLE:
        print("\n== Skipping Prisma connection test (package not available) ==")
        return False
    
    print("\n== Checking Prisma connection ==")
    
    try:
        # Create a Prisma client instance
        print("Initializing Prisma client...")
        prisma = Prisma()
        
        # Connect to the database
        print("Connecting to database...")
        await prisma.connect()
        
        # Execute a simple query
        print("Executing test query...")
        result = await prisma.query_raw("SELECT 1 as test")
        print(f"Query result: {result}")
        
        # Disconnect
        await prisma.disconnect()
        
        print("✓ Prisma connection and query successful")
        return True
    except PrismaError as e:
        print(f"✗ Prisma error: {e}")
        print("  → Check your Prisma configuration and database credentials")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def print_recommendations(successes):
    """Print recommendations based on test results"""
    print("\n== Recommendations ==")
    
    if all(successes.values()):
        print("All tests passed! The database connection is working correctly.")
        return
    
    if not successes.get("hostname", False):
        print("- Check if the database hostname is correct")
        print("- If using Docker, make sure services are on the same network")
        print("- Try using the IP address instead of hostname")
    
    if not successes.get("port", False):
        print("- Verify the database is running and listening on the expected port")
        print("- Check firewall settings to ensure the port is accessible")
        print("- Verify Docker network configuration if applicable")
    
    if not successes.get("prisma", False):
        print("- Check database credentials (username/password)")
        print("- Verify database name exists and is correctly specified")
        print("- Check that Prisma schema matches the database structure")
    
    print("\nFor Docker environments:")
    print("- Make sure the database and app containers are on the same network")
    print("- Check the DATABASE_URL in your docker-compose.yml")
    print("- Try restarting both the database and app containers")
    print("- Verify your Docker network configuration")


async def main():
    print("=== Database Connection Diagnostic Tool ===\n")
    
    # Get database connection info
    db_info = get_db_connection_info()
    
    # Initialize success tracking
    successes = {
        "hostname": False,
        "port": False,
        "prisma": False
    }
    
    # Run tests
    successes["hostname"] = check_hostname_resolution(db_info["host"])
    if successes["hostname"]:
        successes["port"] = check_port_connectivity(db_info["host"], db_info["port"])
    
    # Run network diagnostics if there are problems
    if not (successes["hostname"] and successes["port"]):
        run_network_diagnostics(db_info["host"])
    
    # Check Prisma connection
    successes["prisma"] = await check_prisma_connection(db_info)
    
    # Print recommendations
    print_recommendations(successes)


if __name__ == "__main__":
    asyncio.run(main()) 