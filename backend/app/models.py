from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, create_engine

class ActiveMatch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = Field(default=None)
    last_updated: datetime = Field(default_factory=datetime.now, description="Last time the match was updated")
    match_uuid: str = Field(index=True, unique=True)
    game_map: str = Field(description="Name of the map, e.g. 'Ascent'", nullable=True)
    game_start: datetime = Field(description="Start time of the match", nullable=True)
    game_mode: str = Field(description="Game mode, e.g. 'Unrated'", nullable=True)
    state: str = Field(description="Current state of the match, e.g. 'In Progress'", nullable=True)
    party_owner_score: int = Field(description="Score of the party owner", nullable=True)
    party_owner_enemy_score: int = Field(description="Score of the enemy party owner", nullable=True)
    party_size: int = Field(description="Size of the party", nullable=True)
    players: Optional[List["ActiveMatchPlayer"]] = Relationship(
        back_populates="match",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "select"}
    )

class ActiveMatchPlayer(SQLModel, table=True):
    subject: str = Field(primary_key=True, index=True)
    match_id: int = Field(foreign_key="activematch.id", primary_key=True, index=True)  # Make this part of composite key
    character: str
    team_id: str
    game_name: str
    account_level: Optional[int] = Field(default=None, nullable=True)
    player_card_id: Optional[str] = Field(default=None, nullable=True)
    player_title_id: Optional[str] = Field(default=None, nullable=True)
    preferred_level_border_id: Optional[str] = Field(default=None, nullable=True)
    agent_icon: str
    rank: str
    rr: Optional[int] = Field(default=None, nullable=True)
    leaderboard_rank: Optional[int] = Field(default=None, nullable=True)

    match: Optional["ActiveMatch"] = Relationship(back_populates="players")