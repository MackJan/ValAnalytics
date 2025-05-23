from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, create_engine

class UserAuthentication(SQLModel, table=True):
    """
    Stores user authentication information, including hashed password and disabled status.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    riot_id: Optional[str] = Field(index=True, unique=True)
    authorization: str = Field()
    entitlement: str
    client_platform: str
    client_version: str
    user_agent: str

    disabled: bool = Field(default=False)

class User(SQLModel, table=True):
    """
    Stores one ValorantAnalytics user, including credentials
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    # existing Riot account link
    riot_id: Optional[str] = Field(index=True, unique=True)

    # new fields for authentication:
    username: str = Field(index=True, unique=True)
    hashed_password: str
    disabled: bool = Field(default=False)

    # your existing profile info
    name: str = Field(default=None)
    tag: str = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    # relationship back to matches
    match_players: List["MatchPlayer"] = Relationship(back_populates="user")

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_uuid: str = Field(index=True, unique=True)
    map_name: str
    queue: str
    started_at: datetime
    ended_at: datetime

    teams: List["MatchTeam"] = Relationship(
        back_populates="match",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class MatchTeam(SQLModel, table=True):
    """
    Represents a team within a specific match (e.g., "team1" or "team2").
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    label: str = Field(index=True, description="e.g. 'team1' or 'team2'")

    players: List["MatchPlayer"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"cascade": "all, delete-orphan","lazy": "selectin"}
    )
    match: Match = Relationship(back_populates="teams",sa_relationship_kwargs={"lazy": "selectin"})

class MatchPlayer(SQLModel, table=True):
    """
    Association table for users in matches, including per-match stats and team assignment.
    """
    match_id: int = Field(foreign_key="match.id", primary_key=True)
    player_id: int = Field(foreign_key="user.id", primary_key=True, default=None)
    team_id: Optional[int] = Field(
        default=None,
        foreign_key="matchteam.id",
        index=True,
        nullable=True,
    )

    riot_id: str

    # per-match stats
    kills: int = Field(default=None)
    deaths: int = Field(default=None)
    assists: int = Field(default=None)
    score: int = Field(default=None)
    agent: str = Field(default=None)

    user: Optional[User] = Relationship(back_populates="match_players")
    team: Optional[MatchTeam] = Relationship(back_populates="players")
