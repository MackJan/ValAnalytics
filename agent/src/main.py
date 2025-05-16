import requests
from req import Requests
from match import Match
from user import User
from datetime import datetime, timezone
import re
import json

req = Requests()

base_url = "http://localhost:8000/api"

def main():

    user = User()
    user_data= {
        "riot_id": user.user["puuid"],
        "name": user.user["game_name"],
        "tag": user.user["game_tag"]
    }
    #response = requests.post(f"{base_url}/users/",json=user_data)
    #print(response.content)

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

    m = Match()
    matches_data =[]
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
            "started_at": str(datetime.fromtimestamp(data["matchInfo"]["gameStartMillis"]/1000)),
            "ended_at": str(datetime.fromtimestamp((data["matchInfo"]["gameLengthMillis"]+data["matchInfo"]["gameStartMillis"])/1000)),
            "match_players": data["players"]
        }
        matches_data.append(json.dumps(match))


    response = requests.post(f"{base_url}/matches/bulk/", json=matches_data)
    print(matches_data)
    print(response)
    #print(response.json())
if __name__ == "__main__":
    main()