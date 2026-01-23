#!/usr/bin/env python3
"""
Find the correct RFID protocol port by testing binary M-200 protocol
"""

import os
import socket
import sys

from dotenv import load_dotenv

load_dotenv()

from app.services.m200_protocol import HEAD, build_get_device_info_command


def test_port(ip: str, port: int, timeout: int = 2) -> dict:
    """Test if a port responds to M-200 binary protocol"""
    result = {
        "port": port,
        "open": False,
        "protocol": None,
        "error": None,
        "response_preview": None,
    }

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        result["open"] = True

        # Send M-200 GET_DEVICE_INFO command
        cmd = build_get_device_info_command()
        cmd_bytes = cmd.serialize()
        sock.sendall(cmd_bytes)

        # Read response
        response = sock.recv(1024)
        sock.close()

        if not response:
            result["protocol"] = "empty_response"
            return result

        # Check if it's binary M-200 protocol (starts with 0xCF)
        if response[0] == HEAD:
            result["protocol"] = "M-200_BINARY"
            result["response_preview"] = f"✓ Binary protocol detected (HEAD=0x{HEAD:02X})"
            return result

        # Check if it's JSON/HTTP
        try:
            text = response.decode("ascii", errors="replace")
            if text.startswith("Content-Length:") or text.startswith("HTTP/"):
                result["protocol"] = "JSON/HTTP"
                result["response_preview"] = text[:100] + "..." if len(text) > 100 else text
                return result
            if text.strip().startswith("{"):
                result["protocol"] = "JSON"
                result["response_preview"] = text[:100] + "..." if len(text) > 100 else text
                return result
        except:
            pass

        # Unknown protocol
        result["protocol"] = "UNKNOWN"
        result["response_preview"] = f"First bytes: {response[:20].hex().upper()}"

    except socket.timeout:
        result["error"] = "timeout"
    except ConnectionRefusedError:
        result["error"] = "connection_refused"
    except Exception as e:
        result["error"] = str(e)

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Find correct RFID protocol port")
    parser.add_argument(
        "--ip",
        type=str,
        default=os.getenv("RFID_READER_IP", "169.254.247.1"),
        help="Reader IP address",
    )
    parser.add_argument(
        "--ports",
        type=str,
        default="4001,5000,6000,8080,9090,2022,27011,10001,5678",
        help="Comma-separated list of ports to test",
    )
    parser.add_argument("--timeout", type=int, default=2, help="Timeout per port in seconds")

    args = parser.parse_args()

    ports_to_test = [int(p.strip()) for p in args.ports.split(",")]

    print("=" * 70)
    print(f"Scanning for M-200 Binary Protocol on {args.ip}")
    print("=" * 70)
    print()

    results = []
    for port in ports_to_test:
        print(f"Testing port {port}...", end=" ", flush=True)
        result = test_port(args.ip, port, args.timeout)
        results.append(result)

        if result["error"]:
            print(f"✗ {result['error']}")
        elif not result["open"]:
            print("✗ Closed")
        elif result["protocol"] == "M-200_BINARY":
            print(f"✓✓✓ FOUND! {result['response_preview']}")
        else:
            print(f"⚠ {result['protocol']}: {result['response_preview']}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    binary_ports = [r for r in results if r["protocol"] == "M-200_BINARY"]
    if binary_ports:
        print(f"\n✓ Found {len(binary_ports)} port(s) with M-200 binary protocol:")
        for r in binary_ports:
            print(f"  → Port {r['port']}: {r['response_preview']}")
            print(f"    Set in .env: RFID_READER_PORT={r['port']}")
    else:
        print("\n✗ No ports found with M-200 binary protocol")
        print("\nOpen ports found:")
        open_ports = [r for r in results if r["open"]]
        for r in open_ports:
            print(f"  → Port {r['port']}: {r['protocol']}")
            if r["response_preview"]:
                print(f"    Preview: {r['response_preview'][:80]}...")

        print("\n⚠️  The M-200 might:")
        print("  1. Use a different port (check device documentation)")
        print("  2. Require configuration to enable TCP server")
        print("  3. Use serial connection instead of TCP")
        print("  4. Use HTTP/REST API instead of binary protocol")


if __name__ == "__main__":
    main()
