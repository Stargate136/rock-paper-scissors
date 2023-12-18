import json
import uuid

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        await websocket.close()
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


class WebSocketHandler:
    def __init__(self):
        self.manager = WebSocketManager()
        self.player_id = None

    async def on_connect(self, websocket: WebSocket):
        self.player_id = str(uuid.uuid4())  # Créer un nouvel identifiant unique
        await self.manager.connect(websocket)
        await self.manager.send_message(
            json.dumps({
                "status": "connected",
                "player_id": self.player_id
            }),
            websocket
        )

    async def on_disconnect(self, websocket: WebSocket):
        await self.manager.disconnect(websocket)

    async def on_receive(self, websocket: WebSocket, data: str):
        if data == ...:
            ...
