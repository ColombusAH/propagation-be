"""
WebSocket endpoint for real-time RFID tag scan notifications.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time tag broadcasts."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Dictionary to send as JSON
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
        """Send a message to a specific client."""
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
    
    Clients can:
    - Connect and receive tag scan broadcasts
    - Send commands: {"command": "ping"} to test connection
    
    Messages received:
    - {"type": "tag_scanned", "data": {...}} - Tag scan event
    - {"type": "welcome", "message": "Connected to RFID stream"}
    - {"type": "pong"} - Response to ping
    """
    await manager.connect(websocket)
    
    # Send welcome message
    await manager.send_personal_message({
        "type": "welcome",
        "message": "Connected to RFID tag scan stream",
    }, websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                command = message.get("command", "").lower()
                
                if command == "ping":
                    # Respond to ping
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": message.get("timestamp"),
                    }, websocket)
                elif command == "subscribe":
                    # Client subscribes to tag scans (already subscribed by default)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "message": "Subscribed to tag scan events",
                    }, websocket)
                else:
                    # Unknown command
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown command: {command}",
                    }, websocket)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)


