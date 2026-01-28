"""
Server-Sent Events (SSE) endpoint for real-time notifications.
Simpler than WebSocket, works better with PWA.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Set

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Global set of connected clients (for broadcasting)
connected_clients: Set[asyncio.Queue] = set()


async def event_generator(request: Request, queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """Generate SSE events for a client."""
    try:
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
            
            try:
                # Wait for message with timeout (for keepalive)
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"event: {message['type']}\ndata: {json.dumps(message['data'])}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive ping
                yield f"event: ping\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"
                
    except asyncio.CancelledError:
        pass
    finally:
        # Clean up
        if queue in connected_clients:
            connected_clients.remove(queue)
        logger.info(f"SSE client disconnected. Total clients: {len(connected_clients)}")


@router.get("/events")
async def sse_events(request: Request):
    """
    SSE endpoint for real-time notifications.
    
    Events:
    - theft_alert: When a theft is detected
    - tag_scan: When a tag is scanned
    - ping: Keepalive every 30 seconds
    """
    queue: asyncio.Queue = asyncio.Queue()
    connected_clients.add(queue)
    logger.info(f"New SSE client connected. Total clients: {len(connected_clients)}")
    
    return StreamingResponse(
        event_generator(request, queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


async def broadcast_event(event_type: str, data: dict):
    """Broadcast an event to all connected SSE clients."""
    message = {"type": event_type, "data": data}
    
    for queue in list(connected_clients):
        try:
            await queue.put(message)
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
            connected_clients.discard(queue)
    
    logger.info(f"Broadcasted {event_type} to {len(connected_clients)} clients")


# Helper function to send theft alert
async def send_theft_alert_sse(
    product: str,
    epc: str,
    location: str = "Main Gate",
    alert_id: str = None
):
    """Send a theft alert to all connected clients."""
    if alert_id is None:
        alert_id = f"alert-{int(datetime.now().timestamp())}"
    
    await broadcast_event("theft_alert", {
        "alert_id": alert_id,
        "product": product,
        "tag_epc": epc,
        "location": location,
        "timestamp": datetime.now().isoformat(),
    })
