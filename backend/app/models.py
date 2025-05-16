from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, create_engine

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    riot_id: str = Field(index=True, unique=True)

    name: str
    tag: str
    created_at: datetime = Field(default_factory=datetime.now)

    match_players: List["MatchPlayer"] = Relationship(back_populates="user")

class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_uuid: str = Field(index=True, unique=True)
    map_name: str
    queue: str
    started_at: datetime
    ended_at: datetime

    teams: List["MatchTeam"] = Relationship(back_populates="match")

class MatchTeam(SQLModel, table=True):
    """
    Represents a team within a specific match (e.g., "team1" or "team2").
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    label: str = Field(index=True, description="e.g. 'team1' or 'team2'")

    players: List["MatchPlayer"] = Relationship(back_populates="team")
    match: Match = Relationship(back_populates="teams")

class MatchPlayer(SQLModel, table=True):
    """
    Association table for users in matches, including per-match stats and team assignment.
    """
    match_id: int = Field(foreign_key="match.id", primary_key=True)
    player_id: int = Field(foreign_key="user.id", primary_key=True)
    team_id: Optional[int] = Field(
        default=None,
        foreign_key="matchteam.id",
        index=True,
        nullable=True,
    )

    riot_id: str

    # per-match stats
    kills: Optional[int] = None
    deaths: Optional[int] = None
    assists: Optional[int] = None
    score: Optional[int] = None
    agent: Optional[str] = None

    user: Optional[User] = Relationship(back_populates="match_players")
    team: Optional[MatchTeam] = Relationship(back_populates="players")
