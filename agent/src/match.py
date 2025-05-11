from agent.src import req
#from src.presence import Presence
import user
import urllib3
import logging
urllib3.disable_warnings()

class Match:
    def __init__(self):
        self.requests = req.Requests()
        self.user = user.User()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def get_match_history(self, last:int = 10):
        match_history = self.requests.fetch("pd", f"/match-history/v1/history/{self.user.user['puuid']}", "get")
        match_history = match_history["History"][:last]

        return match_history

    def get_match_details(self, match_id: str) -> {}:
        match = self.requests.fetch("pd",f"/match-details/v1/matches/{match_id}","get")
        match_keys = {"matchId","mapId","queueID","gameStartMillis","gameLengthMillis","players"}

        clean_match = {
            k: v
            for k,v in match["matchInfo"].items()
            if k in match_keys
        }

        wanted_player_keys = {"subject", "gameName","tagLine","partyId","characterId","teamId"}
        clean_players = []

        for p in match["players"]:
            slim = {k:p[k] for k in wanted_player_keys}

            stats = p.get("stats",{})
            slim["kills"] = stats.get("kills",0)
            slim["deaths"] = stats.get("deaths",0)
            slim["assist"] = stats.get("assists",0)
            slim["score"] = stats.get("score",0)

            clean_players.append(slim)

        cleaned = {
            "matchInfo": clean_match,
            "players": clean_players
        }

        return cleaned

m = Match()
#match = m.get_match_history()[0]["MatchID"]
print(m.get_match_details("8b92975b-2d39-47dd-967a-8dbd1c079445"))