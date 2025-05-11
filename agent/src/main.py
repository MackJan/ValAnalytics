import requests
from req import Requests
from match import Match
from user import User

req = Requests()

base_url = "http://localhost:8000/api"

def main():
    user = User()
    user_data= {
        "riot_id": user.user["puuid"],
        "name": user.user["game_name"],
        "tag": user.user["game_tag"]
    }
    response = requests.post(f"{base_url}/users/",json=user_data)
    if response.status_code == 200:
        print("POST Response:", response.json())
    else:
        print("POST Error:", response.status_code, response.text)

    match = Match()

    matches = match.get_match_history()
    matches_data = [
        {}
    ]
if __name__ == "__main__":
    main()