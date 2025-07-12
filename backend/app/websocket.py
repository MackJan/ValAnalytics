import logging
from typing import Dict, List
from fastapi import WebSocket
from .cleanup_service import cleanup_service

class ConnectionManager:
    def __init__(self):
        self.live_conns: Dict[str, List[WebSocket]] = {}
        self.agent_conns: Dict[str, WebSocket] = {}

    async def connect_agent(self, agent_id: str, ws: WebSocket):
        await ws.accept()
        self.agent_conns[agent_id] = ws

    async def connect_frontend(self, match_uuid: str, ws: WebSocket):
        await ws.accept()
        self.live_conns.setdefault(match_uuid, []).append(ws)

    def disconnect_frontend(self, match_uuid: str, ws: WebSocket):
        self.live_conns[match_uuid].remove(ws)

    def disconnect_agent(self, match_uuid: str):
        self.agent_conns.pop(match_uuid, None)

    async def request_data(self, match_uuid: str):
        ws = self.agent_conns.get(match_uuid)
        logging.getLogger(__name__).error(f"Requesting data for match {match_uuid} from agent connection: {ws}")

        if not ws:
            return

        await ws.send_json({"type": "request_data", "match_uuid": match_uuid})

    async def broadcast(self, match_uuid: str, message: dict):
        # Update match activity when we receive data from agent
        await cleanup_service.update_match_activity(match_uuid)

        for conn in self.live_conns.get(match_uuid, []):
            await conn.send_json(message)

manager = ConnectionManager()
