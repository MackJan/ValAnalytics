from dataclasses import dataclass, field
from typing import List, Optional
import json
import dataclasses

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

@dataclass
class Player:
    character: str
    subject: str
    tag_line: str
    party_id: str
    team_id: str
    game_name: str
    kills: int
    deaths: int
    assists: int
    score: int
    rank: str
    rr: Optional[int] = None
    leaderboard_rank: Optional[int] = None


@dataclass
class CurrentMatchPlayer:
    subject: str
    character: str
    team_id: str
    game_name: str
    account_level: Optional[int]
    player_card_id: Optional[str]
    player_title_id: Optional[str]
    preferred_level_border_id: Optional[str]
    agent_icon: str
    rank: str
    rr: Optional[int] = None
    leaderboard_rank: Optional[int] = None

@dataclass
class SingleMatch:
    match_id: str
    game_map: str
    game_length: int
    game_start: int
    queue_id: str
    players: List[Player] = field(default_factory=list)

@dataclass
class CurrentMatch:
    match_id: str
    game_map: str
    game_start: int
    game_mode: str
    state: str
    party_owner_score: int
    party_owner_enemy_score: int
    party_size: int
    players: List[CurrentMatchPlayer] = field(default_factory=list)

@dataclass
class BareMatch:
    match_id: str
    game_start: int
    queue_id: str

@dataclass
class MatchHistory:
    subject: str
    match_ids: List[BareMatch] = field(default_factory=list)

@dataclass
class User:
    puuid: str
    pid: str
    game_name: str
    game_tag: str
    name: str
    region: str