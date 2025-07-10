from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl, Field

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str]

class RiotUserGet(BaseModel):
    riot_id: str

class MatchGet(BaseModel):
    match_uuid: str
    game_start_time: int
    queue: str

class UserNameTag(BaseModel):
    name: str
    tag: str

class RiotUser(BaseModel):
    """
    Data returned from the Riot API when a user is authenticated.
    """
    puuid: str
    pid: str
    name: str
    tag: str
    region: str
    game_name: str

class UserRiotAuthentication(BaseModel):
    """
    Stores user authentication information, including hashed password and disabled status.
    """
    riot_id: str
    authorization: str
    entitlement: str
    client_platform: str
    client_version: str
    user_agent: str

    disabled: bool = Field(default=False)

class UserProfileUpdate(BaseModel):
    riot_id: Optional[str] = None
    name: Optional[str]   = None
    tag: Optional[str]    = None

class UserRegister(BaseModel):
    """
    Data the client must supply when _registering_ a new user.
    """
    username: str
    password: str

class UserCreate(BaseModel):
    """
    Data the client must supply when _registering_ a new user.
    """
    username: str
    password: str

    # if you still want to capture their Riot ID & display name:
    riot_id: Optional[str]
    name: Optional[str]
    tag: Optional[str]

class UserRead(BaseModel):
    """
    Data returned to the client when fetching user info.
    """
    id: int
    username: str
    riot_id: Optional[str]
    name: Optional[str]
    tag: Optional[str]
    disabled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserDB(UserRead):
    """
    Internal schema including the hashed password;
    used by your auth logic, never exposed in APIs.
    """
    hashed_password: str

    class Config:
        from_attributes = True

class MatchPlayerBase(BaseModel):
    riot_id: str
    kills: int
    deaths: int
    assists: int
    score: int
    agent: str


class MatchPlayerCreate(MatchPlayerBase):
    """
    Schema for creating the MatchPlayer association
    """


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
    players: Optional[List[MatchPlayerRead]]
    match: Optional["MatchRead"]

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
    pass


class MatchRead(MatchBase):
    """
    Schema for reading Match
    """
    id: int

    class Config:
        from_attributes = True

class ActiveMatchCreate(BaseModel):
    """Schema for creating a new active match"""
    match_uuid: str

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
