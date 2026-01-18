"""
RFID Command Sniffer / Proxy
----------------------------
Listens on a local port (CLIENT_SIDE_PORT) and forwards traffic to the Real Reader (READER_IP:READER_PORT).
Prints all data in HEX to the console.

Usage:
1. Run this script.
2. Open the Manufacturer Software (Simple_Gate or Access_Demo).
3. In the Software, set IP = 127.0.0.1 and Port = 8888 (CLIENT_SIDE_PORT).
4. Click 'Open', 'Get Param', or 'Inventory'.
5. Watch the console for captured commands!
"""

import socket
import threading
import sys

# Configuration
CLIENT_SIDE_PORT = 8888  # Port for the PC Software to connect to
READER_IP = "192.168.1.200"  # Real Reader IP
READER_PORT = 2022  # Real Reader Command Port


def forward(source, destination, direction):
    """Forward data between sockets and print hex."""
    try:
        while True:
            data = source.recv(4096)
            if len(data) == 0:
                break

            # Print intercepted data
            print(f"[{direction}] {data.hex().upper()}")

            # Forward
            destination.sendall(data)
    except Exception as e:
        print(f"[{direction}] Connection Closed or Error: {e}")
    finally:
        source.close()
        destination.close()


def main():
    # Start Listener
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(("0.0.0.0", CLIENT_SIDE_PORT))
    except Exception as e:
        print(f"❌ Failed to bind port {CLIENT_SIDE_PORT}: {e}")
        return

    server.listen(1)
    print(f"🕵️‍♂️ Sniffer listening on 127.0.0.1:{CLIENT_SIDE_PORT}")
    print(f"➡️  Forwarding to {READER_IP}:{READER_PORT}")
    print("\n👉 Please configure your RFID Software to connect to 127.0.0.1 : 8888")

    while True:
        client_sock, client_addr = server.accept()
        print(f"\n✅ Software Connected from {client_addr}")

        # Connect to Real Reader
        try:
            reader_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            reader_sock.settimeout(5)  # 5s timeout for connection
            reader_sock.connect((READER_IP, READER_PORT))
            reader_sock.settimeout(None)  # Remove timeout for data
            print(f"✅ Connected to Real Reader at {READER_IP}:{READER_PORT}")

            # Start Forwarding Threads
            t1 = threading.Thread(target=forward, args=(client_sock, reader_sock, "APP->READER"))
            t2 = threading.Thread(target=forward, args=(reader_sock, client_sock, "READER->APP"))
            t1.start()
            t2.start()

            t1.join()
            t2.join()
            print("❌ Session Ended. Waiting for new connection...")

        except Exception as e:
            print(f"❌ Failed to connect to Reader: {e}")
            client_sock.close()


if __name__ == "__main__":
    main()
