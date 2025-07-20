import websockets
import json
import asyncio
import datetime
from user import Users
from match import Match
import requests
from datetime import datetime
from req import Requests
import os

req = Requests()

# Use environment variable for base URL, fallback to localhost for development
base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# API Key for authentication
API_KEY = os.getenv("VPT_API_KEY", "vpt_change_this_to_your_api_key")

def get_headers():
    """Get headers with API key authentication"""
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

async def push_match_detail(match: dict):
    # Use WebSocket URL based on environment
    ws_url = os.getenv("WS_BASE_URL", "ws://localhost:8000")
    async with websockets.connect(f"{ws_url}/ws/live/{match.get('match_uuid')}") as ws:
        while True:
            await ws.send(json.dumps(match))

            ack = await ws.recv()
            print(f"Received ACK: {ack}")
            if ack == "ACK":
                print("Match detail pushed successfully.")
                return
            else:
                print("Retrying to push match detail...")
                await asyncio.sleep(1)

            await asyncio.sleep(5)


def post_user_and_match():
    user = Users()
    user_data = {
        "riot_id": user.user["puuid"],
        "name": user.user["game_name"],
        "tag": user.user["game_tag"]
    }
    headers = get_headers()
    response = requests.post(f"{base_url}/users/get-or-create/", json=user_data, headers=headers)
    print(response.content)

    req.get_headers()
    users = requests.get(f"{base_url}/users/", headers=headers)
    user = None
    print(req.puuid)
    print(users)
    for u in users.json():
        print(u)
        if u["riot_id"] == req.puuid:
            user = u

    if user is None:
        print("error")
        return

    m = Match()
    matches = m.get_match_history()
    for match_data in matches:
        data = m.get_match_details(match_data["MatchID"])
        for x in range(len(data["players"])):
            data["players"][x]["riot_id"] = data["players"][x].pop("subject")
            data["players"][x]["agent"] = data["players"][x].pop("characterId")
            data["players"][x]["team_color"] = data["players"][x].pop("teamId")
            data["players"][x]["name"] = data["players"][x].pop("gameName")
            data["players"][x]["tag"] = data["players"][x].pop("tagLine")
        match = {
            "match_uuid": data["matchInfo"]["matchId"],
            "map_name": data["matchInfo"]["mapId"],
            "queue": data["matchInfo"]["queueID"],
            "started_at": str(datetime.fromtimestamp(data["matchInfo"]["gameStartMillis"] / 1000)),
            "ended_at": str(datetime.fromtimestamp(
                (data["matchInfo"]["gameLengthMillis"] + data["matchInfo"]["gameStartMillis"]) / 1000))
        }
        # match = json.dumps(match)
        print(match)
        response = requests.post(f"{base_url}/matches/", json=match, headers=headers).text
        print(response)
        match_id = json.loads(response)["id"]

        team_red = {
            "match_id": match_id,
            "label": "red"
        }
        team_blue = {
            "match_id": match_id,
            "label": "blue"
        }

        team_blue_response = json.loads(
            requests.post(f"{base_url}/matches/{match_id}/teams/", json=team_blue, headers=headers).text)
        print(team_blue_response)
        team_red_response = json.loads(
            requests.post(f"{base_url}/matches/{match_id}/teams/", json=team_red, headers=headers).text)
        print(team_red_response)

        team_id_map = {
            "Red": team_red_response["id"],
            "Blue": team_blue_response["id"]
        }
        for player_data in data["players"]:
            u_data = {
                "riot_id": player_data["riot_id"],
                "name": player_data["name"],
                "tag": player_data["tag"]
            }
            new_user = json.loads(requests.post(f"{base_url}/users/get-or-create/", json=u_data, headers=headers).text)

            player = {
                "match_id": match_id,
                "player_id": new_user["id"],
                "team_id": team_id_map.get(player_data["team_color"]),
                "riot_id": player_data["riot_id"],
                "kills": player_data["kills"],
                "deaths": player_data["deaths"],
                "assists": player_data["assists"],
                "score": player_data["score"],
                "agent":
                    json.loads(requests.get(f"https://valorant-api.com/v1/agents/{player_data["agent"]}").text)["data"][
                        "displayName"]
            }

            new_player = requests.post(f"{base_url}/users/get-or-create/", json=player)
            print(new_player)

    # response = requests.post(f"{base_url}/matches/bulk/", json=matches_data)
    # print(matches_data)
    # print(response)
    # print(response.json())

def post_auth():
    headers = req.get_headers()
    puuid = req.puuid

    data = {
        "riot_id": puuid,
        "authorization": headers["Authorization"],
        "entitlement": headers["X-Riot-Entitlements-JWT"],
        "client_platform": headers["X-Riot-ClientPlatform"],
        "client_version": headers["X-Riot-ClientVersion"],
        "user_agent": headers["User-Agent"],
    }

    response = requests.post(f"{base_url}/users/riot_auth/", json=data, headers=get_headers())
    print(response.text)
