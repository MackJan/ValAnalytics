import time

from agent.src.models import EnhancedJSONEncoder
from datetime import timezone
from agent_helper import *
from presence import Presence, decode_presence
from discord_rpc import DiscordRPC
import asyncio
from constants import *
import dataclasses

req = Requests()

base_url = "http://localhost:8000/api"
ws_url = "ws://localhost:8000/ws/agent"
req.get_headers()
m = Match()
p = Presence(req)
rpc = DiscordRPC()

async def create_active_match_with_players(match_uuid, match_data):
    """Create an active match entry with initial player data in the backend"""
    try:
        # Extract player data from match_data
        players_data = []
        if hasattr(match_data, 'players') and match_data.players:
            players_data = [
                {
                    "subject": player.subject,
                    "character": player.character,
                    "team_id": player.team_id,
                    "game_name": player.game_name,
                    "account_level": player.account_level,
                    "player_card_id": player.player_card_id,
                    "player_title_id": player.player_title_id,
                    "preferred_level_border_id": player.preferred_level_border_id,
                    "agent_icon": player.agent_icon,
                    "rank": player.rank,
                    "rr": player.rr,
                    "leaderboard_rank": player.leaderboard_rank
                }
                for player in match_data.players
            ]

        # Create the match entry via HTTP API call
        payload = {"match_uuid": match_uuid}
        response = requests.post(f"{base_url}/active_matches/", json=payload)

        if response.status_code in [200, 201]:
            active_match = response.json()
            print(f"Successfully created active match entry for {match_uuid}")

            # Store players data to be sent via WebSocket
            # We'll send the complete match data including players via WebSocket
            # The WebSocket handler will process the initial player data
            return True
        else:
            print(f"Failed to create active match: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error creating active match with players: {str(e)}")
        return False

async def end_active_match(match_uuid):
    """End an active match entry in the backend"""
    try:
        # First get the active match ID
        response = requests.get(f"{base_url}/active_matches/")
        if response.status_code == 200:
            active_matches = response.json()
            for match in active_matches:
                if match["match_uuid"] == match_uuid and not match.get("ended_at"):
                    # End this match
                    end_payload = {"ended_at": datetime.now(timezone.utc).isoformat()}
                    end_response = requests.patch(f"{base_url}/active_matches/{match['id']}/", json=end_payload)
                    if end_response.status_code == 200:
                        print(f"Successfully ended active match {match_uuid}")
                        return True
                    break
        print(f"Could not find or end active match {match_uuid}")
        return False
    except Exception as e:
        print(f"Error ending active match: {str(e)}")
        return False

async def send_initial_match_data(ws, match_uuid, match_data):
    """Send initial match data to populate the database"""
    try:
        message = {
            "type": "match_update",
            "match_uuid": match_uuid,
            "data": match_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        await ws.send(json.dumps(message, cls=EnhancedJSONEncoder))
        print(f"Sent initial match data for {match_uuid}")
        return True
    except Exception as e:
        print(f"Error sending initial match data: {str(e)}")
        return False

async def run_agent():
    match_uuid = None
    ws = None
    last_update = None
    last_rpc_update = None
    req.get_headers()

    message_queue = asyncio.Queue()

    def dicts_differ(d1, d2):
        if isinstance(d1, dict) and isinstance(d2, dict):
            if d1.keys() != d2.keys():
                return True
            for k in d1:
                if dicts_differ(d1[k], d2[k]):
                    return True
            return False
        return d1 != d2

    async def handle_ws_messages(ws):
        while True:
            try:
                raw = await ws.recv()
                msg = json.loads(raw) if raw != "ACK" else "ACK"

                if msg == "ACK":
                    # Put acknowledgment in queue
                    await message_queue.put("ACK")
                elif msg.get("type") == "request_data":
                    try:
                        if match_uuid and last_update:
                            update_message = {
                                "type": "match_update",
                                "match_uuid": match_uuid,
                                "data": last_update,  # Send the object directly, not JSON string
                                "timestamp": datetime.now(timezone.utc).isoformat()
                            }

                            await ws.send(json.dumps(update_message, cls=EnhancedJSONEncoder))
                            print(f"Sent data in response to request for match {match_uuid}")
                    except Exception as e:
                        print(f"Error handling request_data: {str(e)}")
                else:
                    print(f"Received message: {msg}")
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed in message handler")
                break
            except Exception as e:
                print(f"Error in message handler: {str(e)}")
                break

    while True:
        presence = p.get_presence()
        game_state = p.get_game_state(presence)
        if game_state is None or game_state == "None":
            print("No game state found, waiting for presence update...")
            await asyncio.sleep(5)
            continue
        elif game_state == "MENUS":
            print("In menus, waiting for game to start...")

            party_data = decode_presence(p.get_private_presence(p.get_presence()))
            presence_data = {
                "state": "Menus",
                "details": "Party Size: " + str(party_data.get("partySize", 0)) if party_data["isValid"] else "Solo",
                "start": int(datetime.now(timezone.utc).timestamp()),
                "large_image": "logo",
            }

            rpc.set_presence(**presence_data)

            await asyncio.sleep(5)
            continue

        elif game_state == "PREGAME":
            print("In pregame, waiting for match to start...")
            party_data = decode_presence(p.get_private_presence(p.get_presence()))
            presence_data = {
                "state": "Pregame",
                "details": "Party Size: " + str(party_data.get("partySize", 0)) if party_data["isValid"] else "Solo",
                "start": int(datetime.now(timezone.utc).timestamp()),
                "large_image": "logo",
            }

            rpc.set_presence(**presence_data)

            await asyncio.sleep(5)
            pass
        elif game_state == "INGAME":
            try:
                match_data = m.get_current_match_details()

                if match_data is None:
                    print("No match data found, waiting for next update...")
                    await asyncio.sleep(5)
                    continue

                if last_rpc_update is None:
                    last_rpc_update = match_data
                    rpc.set_match_presence(match_data, int(time.time()))

                if  dicts_differ(last_rpc_update, match_data):
                    rpc.set_match_presence(match_data)
                    last_rpc_update = match_data

                if match_data and match_data.match_uuid:
                    current_match_uuid = match_data.match_uuid

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

                        # Create an active match entry in the backend
                        await create_active_match_with_players(match_uuid, match_data)

                        # Send initial match data to populate the database
                        await send_initial_match_data(ws, match_uuid, match_data)
                        last_update = match_data

                        # Wait for acknowledgment of initial data
                        try:
                            response = await asyncio.wait_for(message_queue.get(), timeout=2.0)
                            print(f"Received acknowledgment for initial data: {response}")
                        except asyncio.TimeoutError:
                            print("No acknowledgment received for initial data")

                        # Skip the regular update this time since we just sent initial data
                        await asyncio.sleep(10)
                        continue

                    if last_update is not None:
                        if not dicts_differ(match_data, last_update):
                            print("No new data to send, skipping...")
                            await asyncio.sleep(5)
                            continue


                    message = {
                        "type": "match_update",
                        "match_uuid": match_uuid,
                        "data": match_data,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }

                    await ws.send(json.dumps(message, cls=EnhancedJSONEncoder))
                    last_update = match_data

                    print(f"Sent live data for match {match_uuid}: {message}")
                    print(match_data)
                    # Wait for acknowledgment from the queue
                    try:
                        response = await asyncio.wait_for(message_queue.get(), timeout=1.0)
                        print(f"Received response: {response}")
                    except asyncio.TimeoutError:
                        print("No acknowledgment received")

            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed, will reconnect on next loop")
                ws = None
            except Exception as e:
                print(f"Error in agent loop: {str(e)}")
                ws = None

            await asyncio.sleep(10)
        else:
            # If the game state is not in-game, end the active match
            if match_uuid is not None:
                await end_active_match(match_uuid)
                match_uuid = None

            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_agent())
    # print(json.dumps(m.get_match_details("4c1d989d-d335-4431-b4fb-985bd336baaa"), cls=EnhancedJSONEncoder))