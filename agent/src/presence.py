import base64
import json
import time


def decode_presence(private):
    if "{" not in str(private) and private is not None and str(private) != "":
        dct = json.loads(base64.b64decode(str(private)).decode("utf-8"))
        if dct.get("isValid"):
            return dct
    return {
        "isValid": False,
        "partyId": 0,
        "partySize": 0,
        "partyVersion": 0,
    }


class Presence:
    def __init__(self, Requests):
        self.requests = Requests

    def get_presence(self):
        presences = self.requests.fetch(url_type="local", endpoint="/chat/v4/presences", method="get")
        return presences['presences']

    def get_game_state(self, presences):
        return self.get_private_presence(presences)["sessionLoopState"]

    def get_private_presence(self, presences):
        for presence in presences:
            if presence['puuid'] == self.requests.puuid:
                if presence.get("championId") is not None or presence.get("product") == "league_of_legends":
                    return None
                else:
                    return json.loads(base64.b64decode(presence['private']))

        return None

    def wait_for_presence(self, PlayersPuuids):
        while True:
            presence = self.get_presence()
            for puuid in PlayersPuuids:
                if puuid not in str(presence):
                    time.sleep(1)
                    continue
            break

    def get_party_state(self, party_id: str) -> dict | None:
        data = self.requests.fetch(url_type="glz", endpoint=f"/parties/v1/parties/{party_id}", method="get")
        # in lobby: party state: STATE: DEFAULT QUEUEID: spikerush QUEUE ENTRY TIME: 2025-08-03T11:03:25.733309Z PREVIOUS STATE: LEAVING_MATCHMAKING
        # in queue: party state: STATE: MATCHMAKING QUEUEID: spikerush QUEUE ENTRY TIME: 2025-08-03T11:05:08.18011333Z PREVIOUS STATE: STARTING_MATCHMAKING
        try:
            ret = {
                "state": data["State"],
                "queueId": data["MatchmakingData"]["QueueID"]
            }

            return ret
        except Exception as e:
            print(f"error {e}")
            print(data)
            return {
                "state": "DEFAULT",
                "queueId": "Normal"
            }

    def get_party(self, uuid: str):
        party = self.requests.fetch("glz", f"/parties/v1/players/{uuid}", "get")
        return party["CurrentPartyID"]
