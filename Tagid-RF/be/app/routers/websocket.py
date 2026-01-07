"""
WebSocket endpoint for real-time RFID tag scan notifications.
"""

import json
import logging
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections for real-time RFID tag broadcasts.
    
    This class maintains a list of active WebSocket connections and provides
    methods for broadcasting messages to all clients or sending to specific clients.
    
    Attributes:
        active_connections (List[WebSocket]): List of currently connected WebSocket clients
        
    Example:
        ```python
        manager = ConnectionManager()
        
        # Connect a new client
        await manager.connect(websocket)
        
        # Broadcast to all clients
        await manager.broadcast({
            "type": "tag_scanned",
            "data": tag_data
        })
        
        # Send to specific client
        await manager.send_personal_message(message, websocket)
        
        # Disconnect client
        manager.disconnect(websocket)
        ```
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket (WebSocket): The WebSocket connection to register
            
        Note:
            Automatically accepts the connection and adds it to active_connections
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from active connections.
        
        Args:
            websocket (WebSocket): The WebSocket connection to remove
            
        Note:
            Safe to call even if websocket is not in active_connections
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(
                f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
            )

    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected WebSocket clients.
        
        Sends the same message to all active connections. Automatically removes
        any connections that fail to receive the message.

        Args:
            message (dict): Dictionary to send as JSON to all clients
            
        Example:
            ```python
            await manager.broadcast({
                "type": "tag_scanned",
                "data": {
                    "epc": "E2806810000000001234ABCD",
                    "rssi": -45
                }
            })
            ```
            
        Note:
            - Does nothing if no clients are connected
            - Automatically removes disconnected clients
            - Errors are logged but don't stop broadcast to other clients
        """
        if not self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific WebSocket client.
        
        Args:
            message (dict): Dictionary to send as JSON
            websocket (WebSocket): Target WebSocket connection
            
        Example:
            ```python
            await manager.send_personal_message(
                {"type": "welcome", "message": "Hello!"},
                websocket
            )
            ```
            
        Note:
            - Automatically disconnects client if send fails
            - Errors are logged
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Error sending personal message: {e}")
            self.disconnect(websocket)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/rfid")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time RFID tag scan notifications.
    
    Provides a persistent bidirectional connection for receiving real-time RFID tag
    scan events. Clients connect once and receive continuous updates as tags are scanned.
    
    Connection URL:
        ws://localhost:8000/ws/rfid (development)
        wss://your-domain.com/ws/rfid (production)
        
    Connection Flow:
        1. Client connects to /ws/rfid
        2. Server sends welcome message
        3. Client is automatically subscribed to tag scan events
        4. Server broadcasts tag_scanned events when tags are detected
        5. Client can send commands (ping, subscribe)
        6. Connection remains open until client disconnects
        
    Client-to-Server Messages (Commands):
        ```json
        // Ping - test connection
        {"command": "ping", "timestamp": "2026-01-06T12:00:00Z"}
        
        // Subscribe - explicitly subscribe (already subscribed by default)
        {"command": "subscribe"}
        ```
        
    Server-to-Client Messages (Events):
        ```json
        // Welcome message (sent on connection)
        {
            "type": "welcome",
            "message": "Connected to RFID tag scan stream"
        }
        
        // Tag scanned event (broadcast to all clients)
        {
            "type": "tag_scanned",
            "data": {
                "id": 123,
                "epc": "E2806810000000001234ABCD",
                "tid": "E200001234567890",
                "rssi": -45,
                "antenna_port": 1,
                "location": "Warehouse A",
                "read_count": 5,
                "first_seen": "2026-01-06T10:00:00Z",
                "last_seen": "2026-01-06T12:00:00Z",
                "is_active": true
            }
        }
        
        // Pong response (reply to ping)
        {
            "type": "pong",
            "timestamp": "2026-01-06T12:00:00Z"
        }
        
        // Subscription confirmation
        {
            "type": "subscribed",
            "message": "Subscribed to tag scan events"
        }
        
        // Error message
        {
            "type": "error",
            "message": "Invalid JSON format"
        }
        ```
        
    JavaScript Client Example:
        ```javascript
        // Connect to WebSocket
        const ws = new WebSocket('ws://localhost:8000/ws/rfid');
        
        ws.onopen = () => {
            console.log('Connected to RFID stream');
            
            // Send ping to test connection
            ws.send(JSON.stringify({
                command: 'ping',
                timestamp: new Date().toISOString()
            }));
        };
        
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            
            switch(message.type) {
                case 'welcome':
                    console.log(message.message);
                    break;
                    
                case 'tag_scanned':
                    console.log('Tag detected:', message.data.epc);
                    // Update UI with new tag
                    updateTagList(message.data);
                    break;
                    
                case 'pong':
                    console.log('Connection alive');
                    break;
                    
                case 'error':
                    console.error('Error:', message.message);
                    break;
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        ws.onclose = () => {
            console.log('Disconnected from RFID stream');
            // Implement reconnection logic
        };
        ```
        
    Python Client Example:
        ```python
        import asyncio
        import websockets
        import json
        
        async def listen_to_tags():
            uri = "ws://localhost:8000/ws/rfid"
            
            async with websockets.connect(uri) as websocket:
                # Receive welcome message
                welcome = await websocket.recv()
                print(f"Server: {welcome}")
                
                # Listen for tag scans
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data['type'] == 'tag_scanned':
                        tag = data['data']
                        print(f"Tag scanned: {tag['epc']} (RSSI: {tag['rssi']})")
        
        asyncio.run(listen_to_tags())
        ```
        
    Notes:
        - All connected clients receive the same tag scan events (broadcast)
        - Connection is persistent - remains open until client disconnects
        - Automatic reconnection should be implemented on the client side
        - Tag scan events are triggered by POST /api/v1/tags/ or continuous scanning
        - Maximum message size is limited by FastAPI defaults (16MB)
        - Heartbeat/ping recommended every 30-60 seconds to keep connection alive
        - WebSocket connections don't require authentication in current implementation
        
    Raises:
        WebSocketDisconnect: Client disconnected (handled gracefully)
        Exception: Unexpected error (logged and connection closed)
    """
    await manager.connect(websocket)

    # Send welcome message
    await manager.send_personal_message(
        {
            "type": "welcome",
            "message": "Connected to RFID tag scan stream",
        },
        websocket,
    )

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                command = message.get("command", "").lower()

                if command == "ping":
                    # Respond to ping
                    await manager.send_personal_message(
                        {
                            "type": "pong",
                            "timestamp": message.get("timestamp"),
                        },
                        websocket,
                    )
                elif command == "subscribe":
                    # Client subscribes to tag scans (already subscribed by default)
                    await manager.send_personal_message(
                        {
                            "type": "subscribed",
                            "message": "Subscribed to tag scan events",
                        },
                        websocket,
                    )
                else:
                    # Unknown command
                    await manager.send_personal_message(
                        {
                            "type": "error",
                            "message": f"Unknown command: {command}",
                        },
                        websocket,
                    )

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON format",
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)
