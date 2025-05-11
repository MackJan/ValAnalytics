import requests
from req import Requests
from match import Match
from user import User
import datetime
import re
import json

req = Requests()

base_url = "http://localhost:8000/api"

def main():
    """
    user = User()
    user_data= {
        "riot_id": user.user["puuid"],
        "name": user.user["game_name"],
        "tag": user.user["game_tag"]
    }
    response = requests.post(f"{base_url}/users/",json=user_data)
    if response.status_code == 200:
        print("POST Response:", response.json())
        user_id = response.json()["id"]
    else:
        print("POST Error:", response.status_code, response.text)
        user_id = int(re.search(r'\d+', response.text).group())
    """

    user = requests.get(f"{base_url}/users/").json()[1]

    m = Match()
    matches_data =[]
    matches = m.get_match_history()
    for match_data in matches:
        data = m.get_match_details(match_data["MatchID"])
        match = {
            "match_uuid": data["matchInfo"]["matchId"],
            "map_name": data["matchInfo"]["mapId"],
            "queue": data["matchInfo"]["queueID"],
            "started_at": str(datetime.datetime.fromtimestamp(data["matchInfo"]["gameStartMillis"]/1000)),
            "ended_at": str(datetime.datetime.fromtimestamp((data["matchInfo"]["gameLengthMillis"]+data["matchInfo"]["gameStartMillis"])/1000))
        }
        matches_data.append(match)

    response = requests.post(f"{base_url}/users/{user["id"]}/matches/", json=matches_data)
    if response.status_code == 200:
        print("POST Response:", response.json())
        user_id = response.json()["id"]
    else:
        print("POST Error:", response.status_code, response.text)
        user_id = int(re.search(r'\d+', response.text).group())
if __name__ == "__main__":
    main()