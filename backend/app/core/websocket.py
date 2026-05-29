import asyncio
from collections import defaultdict
from typing import Any, DefaultDict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: DefaultDict[int, List[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(user_id, [])
        self.active_connections[user_id] = [conn for conn in connections if conn != websocket]
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: Any, user_id: int) -> None:
        connections = list(self.active_connections.get(user_id, []))
        if not connections:
            return
        await asyncio.gather(
            *(connection.send_json(message) for connection in connections),
            return_exceptions=True,
        )


connection_manager = ConnectionManager()
