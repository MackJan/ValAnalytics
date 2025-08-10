import req
from user import Users
from match import Match
from name_service import get_map_name, get_agent_name, get_gamemodes_from_codename

class Pregame:
    def __init__(self):
        self.requests = req.Requests()
        self.user = Users()
        self.match = Match()

    def get_pregame_match_id(self):
        data = self.requests.fetch("glz",f"/pregame/v1/players/{self.user.user.puuid}","get")

        try:
            return data["MatchID"]
        except:
            return None

    def get_pregame_data(self):
        match_id = self.get_pregame_match_id()
        if match_id is None:
            return None

        try:
            data = self.requests.fetch("glz",f"/pregame/v1/matches/{match_id}","get")
            player = None
            for p in data["AllyTeam"]["Players"]:
                if p["Subject"] == self.user.user.puuid:
                    player = p
                    break

            return {
                "Map": get_map_name(data["MapID"]),
                "CharacterId": player["CharacterID"],
                "CharacterSelectionState": player["CharacterSelectionState"],
                "TimeRemainingNS": data["PhaseTimeRemainingNS"],
                "Mode": get_gamemodes_from_codename(data["QueueID"])
            }
        except:
            return None

    def get_pregame_info(self):
        data = self.get_pregame_data()
        if data is None:
            return None
        ret = {
            "Map": data["Map"],
            "Character": get_agent_name(data["CharacterId"]),
            "CharacterSelectionState": data["CharacterSelectionState"],
            "Mode": data["Mode"]
        }

        return ret
