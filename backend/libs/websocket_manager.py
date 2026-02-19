from fastapi import WebSocket
from typing import List, Dict, Set
import json
from libs.logger import get_logger

logger = get_logger(__name__)

class ConnectionManager:
    def __init__(self):
        # session_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # session_id -> game state / config (optional cache)
        self.session_states: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"Client connected to session {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
            logger.info(f"Client disconnected from session {session_id}")

    async def broadcast(self, message: dict, session_id: str, exclude: WebSocket = None):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting to client: {e}")

manager = ConnectionManager()
