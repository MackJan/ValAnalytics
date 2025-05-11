from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    riot_id: str = Field(index=True, unique=True)
    name: str
    tag: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Through association table for players in matches
    match_players: List["MatchPlayer"] = Relationship(back_populates="player")


class Match(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_uuid: str = Field(index=True, unique=True)
    map_name: str
    queue: str
    started_at: datetime
    ended_at: datetime

    # Teams participating in this match
    teams: List["MatchTeam"] = Relationship(back_populates="match")

    # Players and their stats for this match
    match_players: List["MatchPlayer"] = Relationship(back_populates="match")

    # Rounds of this match
    rounds: List["Round"] = Relationship(back_populates="match")


class MatchTeam(SQLModel, table=True):
    """
    Represents a team within a specific match (e.g., "team1" or "team2").
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    label: str = Field(index=True, description="e.g. 'team1' or 'team2'")

    match: Match = Relationship(back_populates="teams")
    team_players: List["MatchPlayer"] = Relationship(back_populates="team")


class MatchPlayer(SQLModel, table=True):
    """
    Association table for users in matches, including per-match stats and team assignment.
    """
    match_id: int = Field(foreign_key="match.id", primary_key=True)
    player_id: int = Field(foreign_key="user.id", primary_key=True)
    team_id: Optional[int] = Field(foreign_key="matchteam.id", index=True)

    # per-match stats
    kills: Optional[int] = None
    deaths: Optional[int] = None
    assists: Optional[int] = None
    score: Optional[int] = None
    agent: Optional[str] = None

    # relationships
    match: Match = Relationship(back_populates="match_players")
    player: User = Relationship(back_populates="match_players")
    team: Optional[MatchTeam] = Relationship(back_populates="team_players")


class Round(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    number: int
    winner: str
    timestamp: datetime = Field(default_factory=datetime.now)

    match: Match = Relationship(back_populates="rounds")
    events: List["Event"] = Relationship(back_populates="round")


class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    round_id: int = Field(foreign_key="round.id", index=True)
    type: str
    actor: str
    target: Optional[str]
    value: Optional[int]
    timestamp: datetime = Field(default_factory=datetime.now)

    round: Round = Relationship(back_populates="events")
