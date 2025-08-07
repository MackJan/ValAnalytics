import datetime

import req
from user import Users
import urllib3
import logging
from presence import Presence
from name_service import get_map_name, get_agent_name, get_name_from_puuid, get_multiple_names_from_puuid, \
    get_agent_icon
from models import *
from constants import *
import time

urllib3.disable_warnings()


class Match:
    def __init__(self):
        self.requests = req.Requests()
        self.user = Users()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.presence = Presence(self.requests)

        user_rank, _ = self.get_rank_by_uuid(self.user.user.puuid)
        self.user.user.rank = user_rank["rank"]
        self.user.user.rr = user_rank["rr"]
        self.match_start = {}

    def get_own_match_history(self, last: int = 10) -> MatchHistory:
        match_history = self.requests.fetch("pd", f"/match-history/v1/history/{self.user.user.puuid}", "get")
        match_history = match_history["History"][:last]
        matches = [
            BareMatch(
                match_uuid=m["MatchID"],
                game_start=m["GameStartTime"],
                queue_id=m["QueueID"],
            )
            for m in match_history
        ]

        return MatchHistory(match_ids=matches, subject=self.user.user.puuid)

    def get_current_match_details(self, init: bool = False) -> (Optional[CurrentMatch], Optional[CurrentMatchPlayer]):

        match_id = self.get_current_match_id()
        if not match_id:
            self.logger.debug("No current match found.")
            return None

        if match_id not in self.match_start.keys():
            self.match_start = {match_id: datetime.datetime.now().isoformat()}

        presence = self.presence.get_private_presence(self.presence.get_presence())
        data = self.requests.fetch("glz", f"/core-game/v1/matches/{match_id}", "get")

        match_stats = {
            k: v
            for k, v in presence.items()
            if k in {"sessionLoopState", "matchMap", "partySize", "partyOwnerMatchScoreAllyTeam",
                     "partyOwnerMatchScoreEnemyTeam"}
        }

        players = []
        player = None
        puuids = [p["Subject"] for p in data["Players"]]
        names = get_multiple_names_from_puuid(puuids, self.requests)

        for p in data["Players"]:
            if p["Subject"] == self.user.user.puuid:
                player = CurrentMatchPlayer(
                    subject=p["Subject"],
                    character=get_agent_name(p["CharacterID"]),
                    team_id=p["TeamID"],
                    game_name=names.get(p["Subject"], "Unknown Player"),
                    account_level=p["PlayerIdentity"].get("AccountLevel"),
                    player_card_id=p["PlayerIdentity"].get("PlayerCardID"),
                    player_title_id=p["PlayerIdentity"].get("PlayerTitleID"),
                    preferred_level_border_id=p["SeasonalBadgeInfo"].get("PreferredLevelBorderID"),
                    agent_icon=get_agent_icon(p["CharacterID"]),
                    rank="placeholder"
                )

        if init:
            party_owner_average_rank_num = 0
            party_owner_players = 0
            party_owner_enemy_average_rank_num = 0
            party_owner_enemy_players = 0

            for p in data["Players"]:
                rank, rank_num = self.get_rank_by_uuid(p["Subject"])

                players.append(
                    CurrentMatchPlayer(
                        subject=p["Subject"],
                        character=get_agent_name(p["CharacterID"]),
                        team_id=p["TeamID"],
                        game_name=names.get(p["Subject"], "Unknown Player"),
                        account_level=p["PlayerIdentity"].get("AccountLevel"),
                        player_card_id=p["PlayerIdentity"].get("PlayerCardID"),
                        player_title_id=p["PlayerIdentity"].get("PlayerTitleID"),
                        preferred_level_border_id=p["SeasonalBadgeInfo"].get("PreferredLevelBorderID"),
                        agent_icon=get_agent_icon(p["CharacterID"]),
                        rank=rank["rank"],
                        rr=rank["rr"],
                    )
                )

                if p["TeamID"] == player.team_id:
                    if rank_num != 0:
                        party_owner_average_rank_num += rank_num
                        party_owner_players += 1
                else:
                    if rank_num != 0:
                        party_owner_enemy_average_rank_num += rank_num
                        party_owner_enemy_players += 1

            party_owner_enemy_average_rank = self.get_rank_by_id(
                int(party_owner_enemy_average_rank_num / party_owner_enemy_players if party_owner_enemy_players != 0 else 0))[
                "tierName"]
            party_owner_average_rank = \
                self.get_rank_by_id(int(party_owner_average_rank_num / party_owner_players if party_owner_players != 0 else 0))["tierName"]

        return CurrentMatch(
            match_uuid=data["MatchID"],
            game_map=get_map_name(data["MapID"]),
            game_start=self.match_start[data["MatchID"]],
            game_mode=self.get_current_gamemode(),
            state=data["State"],
            party_owner_score=match_stats.get("partyOwnerMatchScoreAllyTeam", 0),
            party_owner_enemy_score=match_stats.get("partyOwnerMatchScoreEnemyTeam", 0),
            party_owner_average_rank=party_owner_average_rank if init else None,
            party_owner_enemy_average_rank=party_owner_enemy_average_rank if init else None,
            party_owner_team_id=player.team_id,
            party_size=match_stats.get("partySize", 1),
            players=players,
        ), player

    def get_match_details(self, match_id: str) -> SingleMatch:
        match = self.requests.fetch("pd", f"/match-details/v1/matches/{match_id}", "get")
        match_info = match["matchInfo"]
        players = [
            Player(
                character=p["characterId"],
                subject=p["subject"],
                tag_line=p["tagLine"],
                party_id=p["partyId"],
                team_id=p["teamId"],
                game_name=p["gameName"],
                kills=p.get("stats", {}).get("kills", 0),
                deaths=p.get("stats", {}).get("deaths", 0),
                assists=p.get("stats", {}).get("assists", 0),
                score=p.get("stats", {}).get("score", 0),
                rank=self.get_rank_by_id(p["competitiveTier"]),

            )
            for p in match["players"]
        ]

        return SingleMatch(
            match_uuid=match_info["matchId"],
            game_map=match_info["mapId"],
            game_length=match_info["gameLengthMillis"],
            game_start=match_info["gameStartMillis"],
            queue_id=match_info["queueID"],
            players=players,
        )

    def get_current_match_id(self) -> str:
        match = self.requests.fetch("glz", f"/core-game/v1/players/{self.user.user.puuid}", "get")

        if match and "MatchID" in match:
            return match["MatchID"]

        raise Exception("Could not find current match ID. Make sure you are in a match.")

    def get_current_gamemode(self):
        presence_data_raw = self.presence.get_private_presence(self.presence.get_presence())
        gamemode = gamemodes.get(presence_data_raw["queueId"])
        return gamemode

    def get_rank_by_id(self, rank_id: int):
        return ranks.get(rank_id, "Unranked")

    def get_rank_by_uuid(self, uuid: str) -> (dict, int):

        try:
            data = self.requests.fetch("pd", f"/mmr/v1/players/{uuid}", "get")
            if not data:
                return {"rank": "Unranked", "rr": None}
            latest_rank = data["LatestCompetitiveUpdate"]["TierAfterUpdate"]
            latest_rr = data["LatestCompetitiveUpdate"]["RankedRatingAfterUpdate"]

            ret = {
                "rank": self.get_rank_by_id(latest_rank).get("tierName", "Unranked"),
                "rr": latest_rr,
            }
            return ret, latest_rank

        except Exception:
            return {"rank": "Unranked", "rr": None}, 0
