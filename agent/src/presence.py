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
            print(self.requests.puuid)
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