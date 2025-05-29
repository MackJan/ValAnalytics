import requests
from req import Requests
from match import Match
from user import User
from datetime import datetime, timezone
import re
import json
import websocket
import threading
import time
from websocket_helper import *

req = Requests()

base_url = "http://localhost:8000/api"


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
        await asyncio.gather(listener())

def collect_live_stats():
    # read from Valorant local API...
    return {"kills": 5, "deaths": 1, "assists": 0}


def post_user_and_match():
    user = User()
    user_data = {
        "riot_id": user.user["puuid"],
        "name": user.user["game_name"],
        "tag": user.user["game_tag"]
    }
    response = requests.post(f"{base_url}/users/get-or-create/", json=user_data)
    print(response.content)

    req.get_headers()
    users = requests.get(f"{base_url}/users/")
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
    headers = {'Content-type': 'application/json'}

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

    response = requests.post(f"{base_url}/users/riot_auth/", json=data)
    print(response.text)

def post_current_match():
    m = Match()
    match = m.get_current_match()
    if not match:
        print("No current match found.")
        return

    match_data = {
        "match_uuid": match["matchInfo"]["matchId"],
        "map_name": match["matchInfo"]["mapId"],
        "queue": match["matchInfo"]["queueID"],
        "started_at": str(datetime.fromtimestamp(match["matchInfo"]["gameStartMillis"] / 1000)),
        "ended_at": str(datetime.fromtimestamp(
            (match["matchInfo"]["gameLengthMillis"] + match["matchInfo"]["gameStartMillis"]) / 1000))
    }

    push_match_detail(match_data)


if __name__ == "__main__":
    asyncio.run(agent_loop())

