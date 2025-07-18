import datetime
import logging
import time

from agent.src.models import EnhancedJSONEncoder
from datetime import timezone
from agent_helper import *
from presence import Presence, decode_presence
from discord_rpc import DiscordRPC
import asyncio
from constants import *
import dataclasses
from models import CurrentMatch, CurrentMatchPlayer
import logging

req = Requests()

base_url = "http://localhost:8000/api"
ws_url = "ws://localhost:8000/ws/agent"
req.get_headers()
m = Match()
p = Presence(req)
rpc = DiscordRPC()


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create logger properly
logger = logging.getLogger(__name__)

async def create_active_match_via_api(match_data: CurrentMatch):
    """
    Create an active match with players via API call
    """
    # Prepare the payload for the API

    game_start_dt = datetime.fromtimestamp(match_data.game_start, tz=timezone.utc) if match_data.game_start else None


    payload = {
        "match_uuid": match_data.match_uuid,
        "game_map": match_data.game_map,
        "game_start": game_start_dt.isoformat() if game_start_dt else None,
        "game_mode": match_data.game_mode,
        "state": match_data.state,
        "party_owner_score": match_data.party_owner_score,
        "party_owner_enemy_score": match_data.party_owner_enemy_score,
        "party_size": match_data.party_size,
        "players": []
    }

    # Process players data
    if match_data.players:
        for player in match_data.players:
            player_data = {
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
            payload["players"].append(player_data)

    response = requests.post(f"{base_url}/active_matches/", json=payload)
    if response.status_code == 201:
        logger.info(f"Successfully created active match entry for {match_data.match_uuid}")
        return True
    elif response.status_code == 400:
        # Match might already exist, that's okay
        logger.info(f"Active match {match_data.match_uuid} already exists")
        return True
    else:
        logger.error(f"Failed to create active match: {response.status_code} - {response.text}")
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
                        logger.info(f"Successfully ended active match {match_uuid}")
                        return True
                    break
        logger.error(f"Could not find or end active match {match_uuid}")
        return False
    except Exception as e:
        logger.error(f"Error ending active match: {str(e)}")
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
        logger.info(f"Sent initial match data for {match_uuid}")
        return True
    except Exception as e:
        logger.error(f"Error sending initial match data: {str(e)}")
        return False

async def run_agent():
    match_uuid = None
    ws = None
    last_update = None
    last_rpc_update = None
    init = True
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
                            logger.info(f"Sent data in response to request for match {match_uuid}")
                    except Exception as e:
                        logger.error(f"Error handling request_data: {str(e)}")
                        raise e
                else:
                    logger.info(f"Received message: {msg}")
            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket connection closed in message handler")
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {raw}")
                logger.error(f"Error in message handler: {str(e)}")
                raise e
                break

    while True:
        presence = p.get_presence()
        game_state = p.get_game_state(presence)
        if game_state is None or game_state == "None":
            logger.info("No game state found, waiting for presence update...")
            await asyncio.sleep(5)
            continue
        elif game_state == "MENUS":
            logger.info("In menus, waiting for game to start...")

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
            logger.info("In pregame, waiting for match to start...")
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
                if last_update is None:
                    match_data = m.get_current_match_details(init=init)
                else:
                    match_data = m.get_current_match_details()
                init = False
                if match_data is None:
                    logger.info("No match data found, waiting for next update...")
                    await asyncio.sleep(5)
                    continue

                # checking if discord rpc is present
                if last_rpc_update is None:
                    last_rpc_update = match_data
                    rpc.set_match_presence(match_data, int(time.time()))

                # if the match data has changed, update the discord rpc
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
                        logger.info(f"Connected to WebSocket for match {match_uuid}")

                        # Start listening for incoming messages
                        asyncio.create_task(handle_ws_messages(ws))

                        # Create an active match entry in the backend
                        await create_active_match_via_api(match_data)

                        # Send initial match data to populate the database
                        await send_initial_match_data(ws, match_uuid, match_data)
                        last_update = match_data

                        # Wait for acknowledgment of initial data
                        try:
                            response = await asyncio.wait_for(message_queue.get(), timeout=2.0)
                            logger.info(f"Received acknowledgment for initial data: {response}")
                        except asyncio.TimeoutError:
                            logger.info("No acknowledgment received for initial data")

                        # Skip the regular update this time since we just sent initial data
                        await asyncio.sleep(10)
                        continue

                    if last_update is not None:
                        if not dicts_differ(match_data, last_update):
                            logger.info("No new data to send, skipping...")
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

                    logger.info(f"Sent live data for match {match_uuid}: {message}")

                    # Wait for acknowledgment from the queue
                    try:
                        response = await asyncio.wait_for(message_queue.get(), timeout=2.0)
                        logger.info(f"Received response: {response}")
                    except asyncio.TimeoutError:
                        logger.warning("No acknowledgment received")

            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket connection closed, will reconnect on next loop")
                ws = None
            except Exception as e:
                logger.error(f"Error in agent loop: {str(e)}")
                ws = None
                raise e

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