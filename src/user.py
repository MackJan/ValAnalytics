from src import req

class User:
    def __init__(self):
        self.requests = req.Requests()
        self.user = self.get_user()
        self.loadout = ""

    def get_user(self):
        session = self.requests.fetch("local","/chat/v1/session","get")
        print(session)

        user = {
            "puuid": session["puuid"],
            "pid": session["pid"],
            "game_name": session["game_name"],
            "game_tag": session["game_tag"],
            "name": session["name"],
            "region": "eu",
        }
        return user
