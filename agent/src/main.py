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
from presence import Presence

req = Requests()

base_url = "http://localhost:8000/api"
ws_url = "ws://localhost:8000/ws/agent"

m = Match()

async def run_agent():
    match_uuid = None
    ws = None
    last_update = None

    async def handle_ws_messages(ws):
        while True:
            try:
                raw = await ws.recv()
                msg = json.loads(raw)
                print(f"Received message: {msg}")
                if msg.get("type") == "request_data":
                    match = m.get_current_match_details()
                    print(f"Current match data: {match}")
                    await ws.send(json.dumps({
                        "type": "match_data",
                        "match_id": msg["match_id"],
                        "frame": match,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }))
                    print("Sent live data in response to request_data")
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed in message handler")
                break
            except Exception as e:
                print(f"Error in message handler: {str(e)}")
                break

    while True:
        try:
            match_data = m.get_current_match_details()
            if match_data and match_data.get("match", {}).get("MatchID"):
                current_match_uuid = match_data["match"]["MatchID"]

                # Only reconnect if match ID changed or connection is closed
                if current_match_uuid != match_uuid or ws is None:
                    # Close previous connection if exists
                    if ws:
                        await ws.close()

                    # Connect to new match
                    match_uuid = current_match_uuid
                    ws = await websockets.connect(f"{ws_url}/{match_uuid}")
                    print(f"Connected to WebSocket for match {match_uuid}")

                    # Start listening for incoming messages
                    asyncio.create_task(handle_ws_messages(ws))

                if last_update is not None:
                    def dicts_differ(d1, d2):
                        if isinstance(d1, dict) and isinstance(d2, dict):
                            if d1.keys() != d2.keys():
                                return True
                            for k in d1:
                                if dicts_differ(d1[k], d2[k]):
                                    return True
                            return False
                        return d1 != d2

                    if not dicts_differ(match_data, last_update):
                        print("No new data to send, skipping...")
                        await asyncio.sleep(5)
                        continue


                message = {
                    "type": "match_update",
                    "match_id": match_uuid,
                    "data": match_data,
                    "ts": datetime.now(timezone.utc).isoformat()
                }

                await ws.send(json.dumps(message))
                last_update = match_data

                print(f"Sent live data for match {match_uuid}")

                # Wait for acknowledgment
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    print(f"Received response: {response}")
                except asyncio.TimeoutError:
                    print("No acknowledgment received")

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed, will reconnect on next loop")
            ws = None
        except Exception as e:
            print(f"Error in agent loop: {str(e)}")
            ws = None

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_agent())

