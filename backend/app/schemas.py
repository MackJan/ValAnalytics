from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl, Field

class ActiveMatchCreate(BaseModel):
    """Schema for creating a new active match"""
    match_uuid: str
    game_map: Optional[str] = None
    game_start: Optional[int] = None
    game_mode: Optional[str] = None
    state: Optional[str] = None
    party_owner_score: Optional[int] = None
    party_owner_enemy_score: Optional[int] = None
    party_owner_average_rank: Optional[str] = None
    party_owner_enemy_average_rank: Optional[str] = None
    party_owner_team_id: Optional[str] = None
    party_size: Optional[int] = None
    players: Optional[List["ActiveMatchPlayerCreate"]] = None

class ActiveMatchPlayerCreate(BaseModel):
    """Schema for creating active match player data"""
    subject: str
    character: str
    team_id: str
    game_name: str
    account_level: Optional[int] = None
    player_card_id: Optional[str] = None
    player_title_id: Optional[str] = None
    preferred_level_border_id: Optional[str] = None
    agent_icon: str
    rank: str
    rr: Optional[int] = None
    leaderboard_rank: Optional[int] = None

class ActiveMatchRead(BaseModel):
    """Schema for reading active match data"""
    id: int
    match_uuid: str
    created_at: datetime
    ended_at: Optional[datetime] = None
    last_updated: datetime
    game_map: Optional[str] = None
    game_start: Optional[datetime] = None
    game_mode: Optional[str] = None
    state: Optional[str] = None
    party_owner_score: Optional[int] = None
    party_owner_enemy_score: Optional[int] = None
    party_owner_average_rank: Optional[str] = None
    party_owner_enemy_average_rank: Optional[str] = None
    party_owner_team_id: Optional[str] = None
    party_size: Optional[int] = None
    players: Optional[List["ActiveMatchPlayerRead"]] = None

class ActiveMatchPlayerRead(BaseModel):
    """Schema for reading active match player data"""
    subject: str
    match_id: int
    character: str
    team_id: str
    game_name: str
    account_level: Optional[int] = None
    player_card_id: Optional[str] = None
    player_title_id: Optional[str] = None
    preferred_level_border_id: Optional[str] = None
    agent_icon: str
    rank: str
    rr: Optional[int] = None
    leaderboard_rank: Optional[int] = None

class ActiveMatchUpdate(BaseModel):
    """Schema for updating active match (mainly for ending matches)"""
    ended_at: Optional[datetime] = None
