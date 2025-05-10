from src import req
#from src.presence import Presence
import user
import requests
import urllib3

class Match:
    def __init__(self):
        self.requests = req.Requests()
        self.user = user.User()

    def get_match_history(self):
        history = self.requests.fetch("pd", f"/match-history/v1/history/{self.user.user['puuid']}", "get")
        print(history)

match = Match()
match.get_match_history()