from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl, Field


class UserRiotAuthentication(BaseModel):
    """
    Stores user authentication information, including hashed password and disabled status.
    """
    riot_id: Optional[str] = Field(index=True, unique=True)
    authorization: str
    entitlement: str
    client_platform: str
    client_version: str
    user_agent: str

    disabled: bool = Field(default=False)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str]

class RiotToken(BaseModel):
    authorization: str

class RiotLoginRequest(BaseModel):
    username: str
    password: str
    hcaptcha_token: str

class RiotIdentity(BaseModel):
    captcha: str
    username: str
    password: str

class RiotAuthRequest(BaseModel):
    type: Literal["auth"]
    language: Literal["en_US"]
    remember: bool
    riot_identity: RiotIdentity


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



