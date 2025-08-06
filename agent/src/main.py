import datetime
import time

from agent.src.name_service import get_map_name
from models import EnhancedJSONEncoder
from datetime import timezone
from presence import Presence, decode_presence
from discord_rpc import DiscordRPC
import asyncio
from req import Requests
from models import CurrentMatch
import logging
from match import Match
import requests
import websockets
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from constants import rpc_game_modes
from pregame import Pregame

load_dotenv()

req = Requests()

base_url = f"http://{os.getenv('BASE_URL')}/api"
ws_url = f"ws://{os.getenv('BASE_URL')}/ws"
web_url = os.getenv("WEB_URL")
# API Key for authentication - get this from backend startup logs
API_KEY = os.getenv("VPT_API_KEY")

req.get_headers()
m = Match()
p = Presence(req)
rpc = DiscordRPC()
pre = Pregame()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create logger properly
logger = logging.getLogger(__name__)


def get_headers():
    """Get headers with API key authentication"""
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }


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
        "party_owner_average_rank": match_data.party_owner_average_rank,
        "party_owner_enemy_average_rank": match_data.party_owner_enemy_average_rank,
        "party_owner_team_id": match_data.party_owner_team_id,
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

    response = requests.post(f"{base_url}/active_matches/", json=payload, headers=get_headers())
    logger.info(f"Creating active match entry for {match_data.match_uuid} with payload: {json.dumps(payload, cls=EnhancedJSONEncoder)}")
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
        end_payload = {"ended_at": datetime.now(timezone.utc).isoformat()}
        end_response = requests.delete(f"{base_url}/active_matches/uuid/{match_uuid}/", json=end_payload,
                                       headers=get_headers())
        if end_response.status_code == 200:
            logger.info(f"Successfully ended active match {match_uuid}")
            return True

        logger.error(
            f"Could not find or end active match {match_uuid}. Status code: {end_response.status_code} - {end_response.text}")
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
    last_game_state = None
    last_match_uuid = None

    active_match_created = False  # Track if we've created the active match via API
    initial_data_sent = False     # Track if we've sent initial WebSocket data
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
                                "data": last_update,
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

    def reset_match_state():
        """Reset all match-related state variables"""
        nonlocal match_uuid, ws, last_update, last_rpc_update, active_match_created, initial_data_sent
        match_uuid = None
        ws = None
        last_update = None
        last_rpc_update = None
        active_match_created = False
        initial_data_sent = False
    party_id = p.get_party(m.user.user.puuid)

    while True:
        presence = p.get_presence()
        game_state = p.get_game_state(presence)

        if game_state is None or game_state == "None":
            logger.info("No game state found, waiting for presence update...")
            await asyncio.sleep(5)
            continue

        elif game_state == "MENUS":
            logger.info("In menus, waiting for game to start...")
            party_state = p.get_party_state(party_id)

            # Clean up when transitioning from INGAME to MENUS
            if last_game_state == "INGAME" and match_uuid is not None:
                await end_active_match(match_uuid)
                if ws:
                    await ws.close()
                reset_match_state()


            last_game_state = "MENUS"
            party_data = decode_presence(p.get_private_presence(p.get_presence()))
            presence_data = {
                "state": "In Menu" if party_state["state"] == "DEFAULT" else "In Queue",
                "details": rpc_game_modes.get(party_state["queueId"]),
                "party_size": [1 if party_data.get("partySize")==0 else party_data.get("partySize"),5],
                "start": int(datetime.now(timezone.utc).timestamp()),
                "large_image": "logo",
            }
            rpc.set_presence(**presence_data)

            await asyncio.sleep(5)
            continue

        elif game_state == "PREGAME":
            logger.info("In pregame, waiting for match to start...")
            pregame_data = pre.get_pregame_info()
            if pregame_data is None:
                await asyncio.sleep(5)
                continue

            last_game_state = "PREGAME"

            party_data = decode_presence(p.get_private_presence(p.get_presence()))
            presence_data = {
                "state": "Party Size: " + str(party_data.get("partySize", 0)) if party_data.get("isValid") else "Solo",
                "details": f"{pregame_data["Mode"]} | Pregame",
                "large_image": pregame_data["Map"].lower(),
                "large_text": f"{pregame_data["Map"]}",
                "small_image": pregame_data["Character"].lower().replace("/", "") if pregame_data["Character"] != "" else None,
                "small_text": f"Locked {pregame_data["Character"]}" if pregame_data["CharacterSelectionState"] == "locked" else f"Selected {pregame_data["Character"]}",
                "party_size": [party_data.get("partySize", 1),5]
            }
            rpc.set_presence(**presence_data)

            await asyncio.sleep(5)
            continue

        elif game_state == "INGAME":
            logger.info("Ingame")
            last_game_state = "INGAME"
            try:
                # Get current match data
                match_data, player = m.get_current_match_details(init=not active_match_created)

                if match_data is None:
                    logger.info("No match data found, waiting for next update...")
                    await asyncio.sleep(5)
                    continue

                current_match_uuid = match_data.match_uuid

                # Handle new match or first time in this match
                if current_match_uuid != match_uuid:
                    # Clean up previous match if exists
                    if match_uuid is not None:
                        await end_active_match(match_uuid)
                        if ws:
                            await ws.close()

                    # Reset state for new match
                    reset_match_state()
                    match_uuid = current_match_uuid

                    # Step 1: Create active match entry via API (only once per match)
                    logger.info(f"Creating new active match entry for {match_uuid}")
                    success = await create_active_match_via_api(match_data)
                    if success:
                        active_match_created = True
                        logger.info(f"Active match created successfully for {match_uuid}")
                    else:
                        logger.error(f"Failed to create active match for {match_uuid}")
                        await asyncio.sleep(5)
                        continue

                    # Step 2: Connect to WebSocket
                    try:
                        ws = await websockets.connect(f"{ws_url}/agent/{match_uuid}?api_key={API_KEY}")
                        logger.info(f"Connected to WebSocket for match {match_uuid}")

                        # Start listening for incoming messages
                        asyncio.create_task(handle_ws_messages(ws))

                        # Step 3: Send initial data via WebSocket (different from API data)
                        if not initial_data_sent:
                            await send_initial_match_data(ws, match_uuid, match_data)
                            initial_data_sent = True
                            last_update = match_data

                            # Wait for acknowledgment
                            try:
                                response = await asyncio.wait_for(message_queue.get(), timeout=2.0)
                                logger.info(f"Received acknowledgment for initial data: {response}")
                            except asyncio.TimeoutError:
                                logger.info("No acknowledgment received for initial data")

                    except Exception as e:
                        logger.error(f"Failed to connect to WebSocket: {str(e)}")
                        await asyncio.sleep(5)
                        continue

                # Handle Discord RPC updates
                if last_rpc_update is None:
                    rpc.set_match_presence(match_data, player=player, start_time=int(time.time()), base_url=web_url)
                    last_rpc_update = match_data
                elif dicts_differ(last_rpc_update, match_data):
                    rpc.set_match_presence(match_data, player=player, base_url=web_url)
                    last_rpc_update = match_data

                # Handle WebSocket updates (only send if data has changed)
                if ws and initial_data_sent:
                    if last_update is None or dicts_differ(match_data, last_update):
                        message = {
                            "type": "match_update",
                            "match_uuid": match_uuid,
                            "data": match_data,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }

                        await ws.send(json.dumps(message, cls=EnhancedJSONEncoder))
                        last_update = match_data
                        logger.info(f"Sent live data update for match {match_uuid}")

                        # Wait for acknowledgment
                        try:
                            response = await asyncio.wait_for(message_queue.get(), timeout=2.0)
                            logger.info(f"Received response: {response}")
                        except asyncio.TimeoutError:
                            logger.warning("No acknowledgment received for update")
                    else:
                        logger.info("No new data to send, skipping WebSocket update...")

            except websockets.exceptions.ConnectionClosed:
                logger.info("WebSocket connection closed, will reconnect on next loop")
                ws = None
                initial_data_sent = False
            except Exception as e:
                logger.error(f"Error in agent loop: {str(e)}")
                ws = None
                initial_data_sent = False

            await asyncio.sleep(5)
        else:
            # Handle other game states - clean up if needed
            if match_uuid is not None:
                await end_active_match(match_uuid)
                if ws:
                    await ws.close()
                reset_match_state()

            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_agent())
    # print(json.dumps(m.get_match_details("4c1d989d-d335-4431-b4fb-985bd336baaa"), cls=EnhancedJSONEncoder))
