from req import Requests
from models import User


class Users:
    def __init__(self, requests: Requests):
        self.requests = requests
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
            region="eu"
        )
        return user

