import asyncio
from enum import Enum

from fastapi import WebSocket


class WebSocketType(Enum):
    ASKING = "asking"
    ANSWERING = "answering"


class ConnectionManager:
    def __init__(self):
        self.asking_list: list[WebSocket] = []
        self.answering_list: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, websocket_type: WebSocketType):
        await websocket.accept()
        match websocket_type:
            case WebSocketType.ASKING:
                self.asking_list.append(websocket)
            case WebSocketType.ANSWERING:
                self.answering_list.append(websocket)

    def disconnect(self, websocket: WebSocket, websocket_type: WebSocketType):
        match websocket_type:
            case WebSocketType.ASKING:
                self.asking_list.remove(websocket)
            case WebSocketType.ANSWERING:
                self.answering_list.remove(websocket)

    async def send_personal_messsage(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


class Mediator:
    def __init__(self):
        self.manager: ConnectionManager = ConnectionManager()
        self.chats: dict = {}  # ключ - спрашивающий, значение - отвечающий

    async def get_answering(self, websocket: WebSocket):
        while True:
            for answering in self.manager.answering_list:
                if answering not in self.chats.values():
                    return answering

            await self.manager.send_personal_messsage(
                "Looking for answering...", websocket
            )
            await asyncio.sleep(1)

    async def get_asking(self, websocket: WebSocket):
        while True:
            for asking, answering in self.chats.items():
                if websocket == answering:
                    return asking

            await asyncio.sleep(1)
