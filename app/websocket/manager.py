import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("aeris.websocket")

class ConnectionManager:
    def __init__(self):
        # Maps client_id -> list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        logger.info(f"WebSocket client connected: {client_id} (Total: {len(self.active_connections[client_id])})")

    def disconnect(self, websocket: WebSocket, client_id: str):
        if client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            payload = json.dumps(message)
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(payload)
                except Exception as e:
                    logger.error(f"Error sending message to {client_id}: {e}")

    async def broadcast(self, event_type: str, data: dict):
        payload = json.dumps({
            "event": event_type,
            "data": data
        })
        # Broadcast to all connected clients
        for client_id, connections in list(self.active_connections.items()):
            for connection in list(connections):
                try:
                    await connection.send_text(payload)
                except Exception as e:
                    logger.warning(f"Failed broadcasting to client {client_id}: {e}")

ws_manager = ConnectionManager()
