"""WebSocket controller for real-time updates."""
import json
import logging
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime

router = APIRouter(tags=["WebSocket"])

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection."""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific client."""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections.discard(connection)
    
    async def broadcast_light_update(self, comodo: str, estado: bool, origem: str):
        """Broadcast light state update."""
        message = {
            "type": "light_update",
            "data": {
                "comodo": comodo,
                "estado": estado,
                "origem": origem
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def broadcast_switch_update(self, nome: str, ativo: bool):
        """Broadcast switch state update."""
        message = {
            "type": "switch_update",
            "data": {
                "nome": nome,
                "ativo": ativo
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def broadcast_event(self, event_type: str, data: dict):
        """Broadcast generic event."""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Clients can receive:
    - light_update: Light state changes
    - switch_update: Switch enable/disable events
    - button_event: Button press events
    - mqtt_event: General MQTT events
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            {
                "type": "connected",
                "data": {"message": "Connected to Smart Heaven WebSocket"},
                "timestamp": datetime.utcnow().isoformat()
            },
            websocket
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                logger.info(f"Received WebSocket message: {message}")
                
                # Echo back for now (can be extended for commands)
                await manager.send_personal_message(
                    {
                        "type": "echo",
                        "data": message,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    websocket
                )
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "data": {"message": "Invalid JSON"},
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    websocket
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
