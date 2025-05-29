import websockets
import json
import asyncio
import datetime

base_url = "ws://localhost:8000/ws"

async def push_match_detail(match: dict):
    async with websockets.connect(base_url) as ws:
        while True:
            await ws.send(json.dumps(match))

            ack  = await ws.recv()
            print(f"Received ACK: {ack}")
            if ack == "ACK":
                print("Match detail pushed successfully.")
                return
            else:
                print("Retrying to push match detail...")
                await asyncio.sleep(1)

            await asyncio.sleep(5)


