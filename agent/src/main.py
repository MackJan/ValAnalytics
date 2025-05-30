import requests
from req import Requests
from match import Match
from user import User
from datetime import datetime, timezone
import re
import json
import websockets
import threading
import time
from agent_helper import *

req = Requests()

base_url = "http://localhost:8000/api"
ws_url = "ws://localhost:8000/ws/agent"

m = Match()
async def agent_loop():
    m = Match()
    uri = "ws://localhost:8000/ws/1"
    async with websockets.connect(uri) as ws:
        #send initial message to establish connection
        await ws.send(json.dumps({"type": "connect", "message": "Agent connected"}))
        print("Connected to WebSocket server")
        async def listener():
            while True:
                raw = await ws.recv()
                msg = json.loads(raw)
                print(f"Received message: {msg}")
                if msg.get("type") == "request_data":
                    match = m.get_current_match_details()
                    print(f"Current match data: {match}")
                    await ws.send(json.dumps({
                        "type": "live_data",
                        "match_id": msg["match_id"],
                        "frame": match,
                        "ts": datetime.datetime.now().isoformat(),
                    }))
                    print("Sent live data in response to request_data")

        async def send_match_details():
            while True:
                match = m.get_current_match_details()
                if match:
                    await ws.send(json.dumps({
                        "type": "match_details",
                        "match_id": match["match"]["MatchID"],
                        "details": match,
                        "ts": datetime.datetime.now(timezone.utc).isoformat(),
                    }))
                    print(f"Sent match details: {match['match']['MatchID']}")
                await asyncio.sleep(10)

        await asyncio.gather(listener(), send_match_details())

async def run_agent():
    match_uuid = None
    ws = None

    while True:
        match_data = m.get_current_match_details()
        if match_data:
            match_uuid = match_data["match"]["MatchID"]
            if ws is None:
                ws = await websockets.connect(f"{ws_url}/{match_uuid}")

            message = {
                "type": "live_data",
                "match_id": match_uuid,
                "data": match_data,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            await ws.send(json.dumps(message))
            print(f"Sent live data for match {match_uuid}: {match_data}")
        time.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_agent())

