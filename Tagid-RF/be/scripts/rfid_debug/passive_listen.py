#!/usr/bin/env python3
"""
Passive listener - just connect and see what the device sends.
Also try simple ASCII commands in case it's a different protocol.
"""

import socket
import sys
import time


def passive_listen(ip: str, port: int, duration: int = 30):
    print("=" * 70)
    print(f"M-200 Passive Listener")
    print(f"Target: {ip}:{port}")
    print(f"Listening for {duration} seconds...")
    print("=" * 70)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        print(f"\nConnecting...")
        sock.connect((ip, port))
        print(f"✓ Connected!")

        # Set short timeout for recv
        sock.settimeout(2)

        start_time = time.time()
        message_count = 0

        print(f"\nListening for incoming data...")
        print("-" * 70)

        while time.time() - start_time < duration:
            try:
                data = sock.recv(4096)
                if data:
                    message_count += 1
                    elapsed = time.time() - start_time
                    print(f"\n[{elapsed:.1f}s] Received {len(data)} bytes:")
                    print(f"  HEX: {data.hex().upper()}")

                    # Try ASCII
                    try:
                        ascii_data = data.decode("ascii", errors="replace")
                        printable = "".join(
                            c if c.isprintable() or c in "\n\r\t" else "." for c in ascii_data
                        )
                        if printable.strip():
                            print(f"  ASCII: {printable[:200]}")
                    except:
                        pass

                    # Check for RFID header
                    if len(data) >= 6 and data[0] == 0xCF:
                        cmd = (data[2] << 8) | data[3]
                        length = data[4]
                        status = data[5] if len(data) > 5 else 0
                        print(f"  RFID Frame: CMD=0x{cmd:04X}, LEN={length}, STATUS=0x{status:02X}")
                else:
                    print("Connection closed by remote")
                    break

            except socket.timeout:
                # Keep listening
                continue
            except Exception as e:
                print(f"Error: {e}")
                break

        print("-" * 70)
        print(f"\nReceived {message_count} messages in {duration} seconds")

        # Now try some simple commands
        print("\n" + "=" * 70)
        print("Trying simple ASCII commands...")
        print("=" * 70)

        test_commands = [
            b"AT\r\n",
            b"VERSION\r\n",
            b"INFO\r\n",
            b"?\r\n",
            b"HELP\r\n",
            b"\r\n",
        ]

        for cmd in test_commands:
            try:
                print(f"\nTX: {repr(cmd)}")
                sock.sendall(cmd)
                sock.settimeout(2)

                response = sock.recv(1024)
                if response:
                    print(f"RX ({len(response)} bytes):")
                    print(f"  HEX: {response.hex().upper()}")
                    try:
                        ascii_resp = response.decode("ascii", errors="replace")
                        print(f"  ASCII: {ascii_resp}")
                    except:
                        pass
                else:
                    print("  (no response)")
            except socket.timeout:
                print("  TIMEOUT")
            except Exception as e:
                print(f"  ERROR: {e}")

            time.sleep(0.5)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("\nSocket closed")


if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    passive_listen(ip, port, duration)
