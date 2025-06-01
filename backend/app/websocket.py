import asyncio
import json
import logging
from typing import Dict, List

import websocket
from fastapi import WebSocket, HTTPException
from starlette.websockets import WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.live_conns: Dict[str, List[WebSocket]] = {}
        self.agent_conns: Dict[str, WebSocket] = {}

    async def connect_agent(self, agent_id: str, ws: WebSocket):
        await ws.accept()
        self.agent_conns[agent_id] = ws

    async def connect_frontend(self, match_id: str, ws: WebSocket):
        await ws.accept()
        self.live_conns.setdefault(match_id, []).append(ws)

    def disconnect_frontend(self, match_uuid: str, ws: WebSocket):
        self.live_conns[match_uuid].remove(ws)

    def disconnect_agent(self, match_id: str):
        self.agent_conns.pop(match_id, None)

    async def request_data(self, match_id: str):
        ws = self.agent_conns.get(match_id)
        logging.getLogger(__name__).error(f"Requesting data for match {match_id} from agent connection: {ws}")

        if not ws:
            return

        await ws.send_json({"type": "request_data", "match_id": match_id})


    async def broadcast(self, match_id: str, message: dict):
        for conn in self.live_conns.get(match_id, []):
            await conn.send_json(message)

manager = ConnectionManager()


