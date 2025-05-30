def get_map_name(map_id: str) -> str:
    """
    Get the map name from the map ID.
    """
    maps = {
        "/Game/Maps/Ascent/Ascent": "Ascent",
        "/Game/Maps/Duality/Duality": "Bind",
        "/Game/Maps/Foxtrot/Foxtrot": "Breeze",
        "/Game/Maps/Canyon/Canyon": "Fracture",
        "/Game/Maps/Triad/Triad": "Haven",
        "/Game/Maps/Port/Port": "Icebox",
        "/Game/Maps/Jam/Jam": "Lotus",
        "/Game/Maps/Pitt/Pitt": "Pearl",
        "/Game/Maps/Bonsai/Bonsai": "Split"
    }
    return maps.get(map_id, map_id)

def get_agent_name(agent_id: str) -> str:
    """
    Get the agent name from the agent ID.
    """
    agents = {
        "5f8d3a7f-467b-97f3-062c-13acf203c006": "Breach",
        "117ed9e3-49f3-6512-3ccf-0cada7e3823b": "Cypher",
        "1e58de9c-4950-5125-93e9-a0aee9f98746": "Killjoy",
        "569fdd95-4d10-43ab-ca70-79becc718b46": "Sage",
        "320b2a48-4d9b-a075-30f1-1f93a9b638fa": "Sova",
        "707eab51-4836-f488-046a-cda6bf494859": "Viper",
        "8e253930-4c05-31dd-1b6c-968525494517": "Omen",
        "eb93336a-449b-9c1b-0a54-a891f7921d69": "Phoenix",
        "add6443a-41bd-e414-f6ad-e58d267f4e95": "Jett",
        "f94c3b30-42be-e959-889c-5aa313dba261": "Raze",
        "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc": "Reyna",
        "6f2a04ca-43e0-be17-7f36-b3908627744d": "Skye",
        "7f94d92c-4234-0a36-9646-3a87eb8b5c89": "Yoru",
        "601dbbe7-43ce-be57-2a40-4abd24953621": "KAY/O"
    }
    return agents.get(agent_id, agent_id)