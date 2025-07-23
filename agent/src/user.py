import req
from models import *

class Users:
    def __init__(self):
        self.requests = req.Requests()
        self.user = self.get_user()
        self.loadout = ""

    def get_user(self)-> User:
        session = self.requests.fetch("local","/chat/v1/session","get")

        user = User(
            puuid=session["puuid"],
            pid=session["pid"],
            game_name=session["game_name"],
            game_tag=session["game_tag"],
            name=session["name"],
            region="eu",
        )
        return user

    def get_party(self):
        party = self.requests.fetch("glz", f"/parties/v1/players/{self.user['puuid']}", "get")
        print(f"#### Party: {party}")
        return party["CurrentPartyID"]