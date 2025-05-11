from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    riot_id: str = Field(index=True, unique=True)
    name: str
    tag: str
    created_at: datetime = Field(default_factory=datetime.now)

    matches: List["Match"] = Relationship(back_populates="player")

class Match(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="user.id", index=True)
    match_uuid: str = Field(index=True, unique=True)
    map_name: str
    agent: str
    queue: str
    started_at: datetime
    ended_at: datetime

    player: User = Relationship(back_populates="matches")
    rounds: List["Round"] = Relationship(back_populates="match")

class Round(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="match.id", index=True)
    number: int
    winner: str
    timestamp: datetime = Field(default_factory=datetime.now)

    match: Match = Relationship(back_populates="rounds")
    events: List["Event"] = Relationship(back_populates="round")

class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    round_id: int = Field(foreign_key="round.id", index=True)
    type: str
    actor: str
    target: Optional[str]
    value: Optional[int]
    timestamp: datetime = Field(default_factory=datetime.now)

    round: Round = Relationship(back_populates="events")