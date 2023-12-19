import base64
import json
import uuid

import matplotlib.pyplot as plt
import numpy as np
import cv2
from fastapi import WebSocket

from .time import TimeManager
from .game import GameManager


class WebSocketManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, player_id: str):
        await websocket.accept()
        self.active_connections[player_id] = websocket

    async def disconnect(self, websocket: WebSocket, player_id: str):
        await websocket.close()
        del self.active_connections[player_id]

    @staticmethod
    async def send_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)


class WebSocketHandler:
    time_manager = TimeManager()
    game_manager = GameManager()
    manager = WebSocketManager()

    def __init__(self):
        self.player_id = None

    async def on_connect(self, websocket: WebSocket):
        self.player_id = str(uuid.uuid4())  # Créer un nouvel identifiant unique
        await self.manager.connect(websocket, self.player_id)
        await self.manager.send_message(
            json.dumps({
                "action": "connect",
                "player_id": self.player_id
            }),
            websocket
        )

    async def on_disconnect(self, websocket: WebSocket):
        # TODO : envoyer un message a l'autre joueur pour indiquer qu'il se déconnecte
        await self.manager.disconnect(websocket, self.player_id)

    async def on_receive(self, websocket: WebSocket, data: dict):
        action = data.get("action")

        if action == "start_game":
            await self.handle_start_game(websocket)
        elif action == "on_click_start_countdown":
            await self.handle_start_countdown(websocket)
        elif action == "capture_webcam":
            image_data = data['image_data'].split(',')[1]
            await self.handle_capture_webcam(websocket, image_data)
        elif action == "get_actual_timestamp":
            await self.handle_get_actual_timestamp(websocket)

    async def handle_start_game(self, websocket: WebSocket):
        game_data = await self.game_manager.add_player_to_queue(self.player_id)
        await self.manager.send_message(
            json.dumps({
                "action": "start_game",
                "player_id": self.player_id,
                "game_data": game_data
            }),
            websocket
        )

    async def handle_start_countdown(self, websocket: WebSocket):
        game = self.game_manager.get_game(self.player_id)
        game.set_player_data(self.player_id, "clicked", True)

        other_player = self.game_manager.get_other_player(self.player_id)
        other_player_clicked = game.get_player_data(other_player, "clicked")
        if other_player_clicked:
            message = json.dumps({
                "action": "start_countdown",
                "start_timestamp": self.time_manager.now(),
                "end_timestamp": self.time_manager.timestamp_after_delay(
                    self.game_manager.DELAY_TO_CAPTURE_IMAGE_IN_SEC
                )
            })
            await self.manager.send_message(message, websocket)
            await self.manager.send_message(message, self.manager.active_connections[other_player])
        else:
            await self.manager.send_message(
                json.dumps({
                    "action": "wait_for_other_player"
                }),
                websocket
            )
            await self.manager.send_message(
                json.dumps({
                    "action": "wait_to_click",
                }),
                self.manager.active_connections[other_player]
            )

    async def handle_capture_webcam(self, websocket: WebSocket, image_data: str):

        image = await self.convert_base64_to_image(image_data)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.show()

        round_winner, round_played, game_status = await self.game_manager.play_round(self.player_id, image)
        print("winner : ", round_winner)
        if not round_played:
            await self.manager.send_message(
                json.dumps({
                    "action": "invalid_image",
                    "image_data": image_data
                }),
                websocket
            )
        else:

            await self.manager.send_message(
                json.dumps({
                    "action": "capture_webcam",
                    "image_data": image_data
                }),
                websocket
            )

    async def handle_get_actual_timestamp(self, websocket: WebSocket):
        timestamp = self.time_manager.now()
        await self.manager.send_message(
            json.dumps({
                "action": "get_actual_timestamp",
                "timestamp": timestamp
            }),
            websocket
        )

    @staticmethod
    async def convert_base64_to_image(image_data: str):
        binary_data = base64.b64decode(image_data)
        image_array = bytearray(binary_data)

        # Utilisez OpenCV pour traiter l'image
        image = cv2.imdecode(np.array(image_array), cv2.IMREAD_UNCHANGED)
        return image
