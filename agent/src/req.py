import os
import base64
import requests
from os import path
import json
import time
from typing import Optional, Dict, Any, Tuple, List


class Requests:
    def __init__(self):
        self.session = requests.Session()
        self.lockfile = self.get_lockfile()
        self.headers: Dict[str, str] = {}
        self.puuid = ""
        self.version = self.get_version()
        self.region = self.get_region()
        self.pd_url = f"https://pd.{self.region[0]}.a.pvp.net"
        self.glz_url = f"https://glz-{self.region[1][0]}.{self.region[1][1]}.a.pvp.net"
        self.region = self.region[0]

    def fetch(self, url_type: str, endpoint: str, method: str, jsonData=None, retries: int = 3):
        for _ in range(retries):
            if not self.headers:
                self.headers = self.get_headers()
            try:
                if url_type == "glz":
                    url = self.glz_url + endpoint
                    response = self.session.request(
                        method,
                        url,
                        headers=self.headers,
                        verify=True,
                        json=jsonData if method.lower() == "put" and jsonData is not None else None,
                    )
                elif url_type == "pd":
                    url = self.pd_url + endpoint
                    response = self.session.request(
                        method,
                        url,
                        headers=self.headers,
                        verify=True,
                        json=jsonData if method.lower() == "put" and jsonData is not None else None,
                    )
                elif url_type == "local":
                    local_headers = {
                        "Authorization": "Basic "
                        + base64.b64encode(("riot:" + self.lockfile["password"]).encode()).decode()
                    }
                    url = f"https://127.0.0.1:{self.lockfile['port']}{endpoint}"
                    response = self.session.request(method, url, headers=local_headers, verify=False)
                elif url_type == "custom":
                    url = endpoint
                    response = self.session.request(
                        method,
                        url,
                        headers=self.headers,
                        verify=True,
                        json=jsonData if method.lower() == "put" and jsonData is not None else None,
                    )
                else:
                    return None

                if response.ok:
                    return response.json()

                if response.status_code in {401, 403}:
                    self.headers = {}

            except requests.RequestException:
                pass

            time.sleep(5)

        print(f"Error fetching {url_type} data: {response.status_code} - {response.text}")
        return None

    def get_version(self):
        data = self.session.get('https://valorant-api.com/v1/version', verify=True)
        version = data.json()
        return version["data"]["riotClientVersion"]

    def get_region(self):
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if '.a.pvp.net/account-xp/v1/' in line:
                    pd_url = line.split('.a.pvp.net/account-xp/v1/')[0].split('.')[-1]
                elif 'https://glz' in line:
                    glz_url = [(line.split('https://glz-')[1].split(".")[0]),
                               (line.split('https://glz-')[1].split(".")[1])]
                if "pd_url" in locals().keys() and "glz_url" in locals().keys():
                    return [pd_url, glz_url]

    def get_lockfile(self):
        try:
            with open(os.path.join(os.path.dirname(__file__),
                                   path.expandvars(r'%LocalAppData%\Riot Games\Riot Client\Config\lockfile')),
                      'r') as input_file:
                data = input_file.read()
                data = data.split(":")
                keys = ["name", "PID", "port", "password", "protocol"]
                return dict(zip(keys, data))
        except FileNotFoundError:
            raise Exception("Lockfile not found, you are not in-game!")

    def get_headers(self):

        localAuthorization = {
            f'Authorization': 'Basic ' + base64.b64encode(('riot:' + self.lockfile["password"]).encode()).decode()}

        data = self.session.get(
            f'https://127.0.0.1:{self.lockfile["port"]}/entitlements/v1/token',
            headers=localAuthorization,
            verify=False,
        )
        entitlements = data.json()
        self.puuid = entitlements["subject"]
        headers = {
            'Authorization': f"Bearer {entitlements['accessToken']}",
            'X-Riot-Entitlements-JWT': entitlements['token'],
            'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
            'X-Riot-ClientVersion': self.get_version(),
            "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
        }
        return headers