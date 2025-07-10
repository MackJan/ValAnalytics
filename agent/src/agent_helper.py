import websockets
import json
import asyncio
import datetime
from user import Users
from match import Match
import requests
from datetime import datetime
from req import Requests
req = Requests()

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


def post_user_and_match():
    user = Users()
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
