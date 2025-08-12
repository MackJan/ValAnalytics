import logging
import time

from req import Requests
from models import CurrentPlayerStats
import datetime

class PlayerStats:
    def __init__(self, requests: Requests):
        self.requests = requests
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.last_pull = None

    def get_stats(self, puuid: str) -> CurrentPlayerStats:
        data = self.requests.fetch("pd",
                                   f"/mmr/v1/players/{puuid}/competitiveupdates?startIndex=0&endIndex=10&queue=competitive",
                                   "get", retries=3, timeout_sec=2)
        kd_sum, hs_sum, adr_sum = 0, 0, 0
        num_games = 0

        for match in data["Matches"][0:5]:
            if match:
                match_stats = self.get_match_stats(uuid=match["MatchID"], puuid=puuid)
                if not match_stats["success"]:
                    break
                num_games += 1
                if match_stats["kd"]:
                    kd_sum += match_stats["kd"]
                if match_stats["hs"]:
                    hs_sum += match_stats["hs"]
                if match_stats["adr"]:
                    adr_sum += match_stats["adr"]

        if num_games != 0:
            hs = int(hs_sum/num_games)
            kd = round(kd_sum/num_games,2)
            adr = int(adr_sum/num_games)

            return CurrentPlayerStats(
                kd=kd,
                adr=adr,
                hs=hs
            )
        else:
            self.logger.warning(f"No valid match stats found for player {puuid}. Returning default stats.")
            return CurrentPlayerStats(
                kd=0,
                adr=0,
                hs=0
            )

    def get_match_stats(self, uuid: str, puuid: str) -> dict:
        try:
            if self.last_pull and datetime.datetime.now() - self.last_pull < datetime.timedelta(seconds=2):
                time.sleep(2)
            data = self.requests.fetch("pd", f"/match-details/v1/matches/{uuid}", "get")

            player = None

            for p in data["players"]:
                if p["subject"] == puuid:
                    player = p
                    break

            kd, hs, adr = None, None, None

            kd = round(player["stats"]["kills"] / player["stats"]["deaths"], 1) if player["stats"]["deaths"] != 0 else \
                player["stats"]["kills"]

            if player["roundDamage"]:
                damage = 0
                for r in player["roundDamage"]:
                    if r["receiver"] != puuid:
                        damage = damage + r["damage"]

                adr = int(damage / player["stats"]["roundsPlayed"]) if player["stats"]["roundsPlayed"] != 0 else None

            total_hits, total_headshots, kills, deaths = 0, 0, 0, 0

            for r in data.get("roundResults", []):
                for player in r.get("playerStats", []):
                    if player["subject"] == puuid:
                        for hits in player.get("damage", []):
                            total_hits += (
                                    hits.get("legshots", 0)
                                    + hits.get("bodyshots", 0)
                                    + hits.get("headshots", 0)
                            )
                            total_headshots += hits.get("headshots", 0)
            hs = int((total_headshots / total_hits) * 100) if total_hits else None

            stats = {
                "success": True,
                "kd": kd,
                "hs": hs,
                "adr": adr
            }

            return stats

        except Exception as e:
            self.logger.error(f"Error fetching match stats for {puuid} in match {uuid}: {e}")
            return {
                "success": False,
                "kd": 0,
                "hs": 0,
                "adr": 0
            }
