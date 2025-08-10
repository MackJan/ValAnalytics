from typing import Any, Dict
import requests
import constants

params = {"isPlayableCharacter": "true", "language": "en-US"}
_agents: Dict[str, Dict[str, str]] = {}


def load_agent_data() -> Dict[str, Dict[str, str]]:
    """Download and cache agent metadata on demand."""
    if not _agents:
        data = requests.get("https://valorant-api.com/v1/agents", params=params).json()
        for a in data.get("data", []):
            _agents[a["uuid"]] = {
                "uuid": a["uuid"],
                "name": a["displayName"],
                "role": a["role"]["displayName"],
                "icon": a["displayIcon"],
            }
    return _agents

def get_map_name(map_id: str) -> str:
    """
    Get the map name from the map ID.
    """
    return constants.maps.get(map_id, map_id)

def get_agent_name(agent_id: str) -> str:
    """
    Get the agent name from the agent ID.
    """
    agents = load_agent_data()
    return agents.get(agent_id, {}).get("name", agent_id)

def get_name_from_puuid(puuid: str, req) -> dict[str, str | Any] | dict[str, str]:
    """
    Get the name from the PUUID.
    """

    data = req.fetch("pd", f"/name-service/v2/players/", "put", jsonData=[puuid])
    return {"Subject": puuid, "Name": data[0]["GameName"], "Tag": data[0]["TagLine"]} if data else {"Subject": puuid, "Name": "", "Tag": ""}

def get_multiple_names_from_puuid(puuids: list[str], req) -> dict[Any, str]:
    """
    Get the names from multiple PUUIDs.
    """
    data = req.fetch("pd", f"/name-service/v2/players/", "put", jsonData=puuids)

    name_dict = {player["Subject"]: f"{player['GameName']}#{player['TagLine']}"
                     for player in data}
    return name_dict

def get_agent_icon(agent_id: str) -> str:
    """
    Get the agent icon from the agent ID.
    """
    agents = load_agent_data()
    return agents.get(agent_id, {}).get("icon", "")

def get_gamemodes_from_codename(codename:str) -> str:
    return constants.gamemodes.get(codename)

def get_rank_by_id(rank_id: int) -> dict:
    return constants.ranks.get(rank_id, "Unranked")

def get_rpc_gamemodes(gamemode:str) -> str:
    return constants.rpc_game_modes.get(gamemode, gamemode)
