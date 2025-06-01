from agent.src import req
#from src.presence import Presence
import user
import urllib3
import logging
from presence import Presence
from name_service import get_map_name, get_agent_name, get_name_from_puuid, get_multiple_names_from_puuid, get_agent_icon

urllib3.disable_warnings()


class Match:
    def __init__(self):
        self.requests = req.Requests()
        self.user = user.User()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.presence = Presence(self.requests)

    def get_match_history(self, last:int = 10):
        match_history = self.requests.fetch("pd", f"/match-history/v1/history/{self.user.user['puuid']}", "get")
        match_history = match_history["History"][:last]

        return match_history

    def get_current_match_details(self) -> {}:
        match_id = self.get_current_match_id()
        if not match_id:
            self.logger.debug("No current match found.")
            return {}
        print(f"Current match ID: {match_id}")

        presence = self.presence.get_private_presence(self.presence.get_presence())

        data = self.requests.fetch("glz", f"/core-game/v1/matches/{match_id}", "get")
        presence_keys = {"sessionLoopState", "matchMap", "partySize", "partyOwnerMatchScoreAllyTeam", "partyOwnerMatchScoreEnemyTeam"}
        match_stats = {
            k: v
            for k, v in presence.items()
            if k in presence_keys
        }

        match_keys = {"MatchID", "State", "MapID", "ModeID", "Players", "MatchmakingData"}

        clean_match = {
            k: v
            for k, v in data.items()
            if k in match_keys
        }
        clean_match["match_stats"] = match_stats
        clean_match["MapID"] = get_map_name(clean_match["MapID"])

        player_keys = {"Subject", "TeamID", "CharacterID", "PlayerIdentity", "SeasonalBadgeInfo"}
        puuids = []
        for p in data["Players"]:
            puuids.append(p["Subject"])

        names = get_multiple_names_from_puuid(puuids, self.requests)

        for x in range(len(clean_match["Players"])):
            clean_match["Players"][x]["Name"] = names.get(clean_match["Players"][x]["Subject"], "Unknown Player")
            clean_match["Players"][x]["AgentIcon"] = get_agent_icon(clean_match["Players"][x]["CharacterID"])
            clean_match["Players"][x]["CharacterID"] = get_agent_name(clean_match["Players"][x]["CharacterID"])


        #clean_players = []
        #for p in data["Players"]:
        #    slim = {k: p[k] for k in player_keys if k in p}
        #    slim["CharacterID"] = get_agent_name(slim["CharacterID"])
        #    slim["Name"] = names.get(p["Subject"], "Unknown Player")

        #    clean_players.append(slim)

        cleaned_info = {
            "match": clean_match,
            #"players": clean_players
        }

        print(f"Cleaned match details: {cleaned_info}")
        return cleaned_info


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
            slim["assists"] = stats.get("assists",0)
            slim["score"] = stats.get("score",0)

            clean_players.append(slim)

        cleaned = {
            "matchInfo": clean_match,
            "players": clean_players
        }

        print(f"Cleaned match details: {cleaned}")
        return cleaned


    def get_current_match(self) -> {}:
        match_id = self.get_current_match_id()
        if not match_id:
            self.logger.debug("No current match found.")
            return {}
        print(f"Current match ID: {match_id}")
        return self.get_match_details(match_id)

    def get_current_match_id(self) -> str:
        match = self.requests.fetch("glz", f"/core-game/v1/players/{self.user.user["puuid"]}", "get")
        print(match)
        if match and "MatchID" in match:
            return match["MatchID"]

        raise Exception("Could not find current match ID. Make sure you are in a match.")