from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    riot_id: str
    name: str
    tag: str


class UserCreate(UserBase):
    """
    Schema for creating a new User
    """
    pass


class UserRead(UserBase):
    """
    Schema for reading User data
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MatchPlayerBase(BaseModel):
    riot_id: str
    kills: int
    deaths: int
    assists: int
    score: int
    agent: str
    team_color:Optional[str]
    name: str
    tag: str


class MatchPlayerCreate(MatchPlayerBase):
    """
    Schema for creating the MatchPlayer association
    """
    team_id: Optional[int]
    team_color: str


class MatchPlayerRead(MatchPlayerBase):
    """
    Schema for reading MatchPlayer
    """
    match_id: int
    player_id: int
    team: Optional["TeamRead"]
    user: Optional[UserRead]

    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    match_id: int
    label: str


class TeamCreate(TeamBase):
    """
    Schema for creating a Team
    """
    pass

class TeamRead(TeamBase):
    """
    Schema for reading Team
    """
    id: int
    players: List[MatchPlayerRead]
    match: "MatchRead"

    class Config:
        from_attributes = True


class MatchBase(BaseModel):
    match_uuid: str
    map_name: str
    queue: str
    started_at: datetime
    ended_at: datetime

class MatchCreate(MatchBase):
    """
    Schema for creating a Match
    """
    match_players: Optional[List[MatchPlayerBase]]
    pass


class MatchRead(MatchBase):
    """
    Schema for reading Match
    """
    id: int

    class Config:
        from_attributes = True



