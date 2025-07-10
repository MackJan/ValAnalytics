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
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
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
    num_used: int = Field(default=0)

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
    name: Optional[str] = Field(default=None)
    tag: Optional[str] = Field(default=None)
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
    players: List["MatchPlayer"] = Relationship(
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
    match_id: int = Field(foreign_key="match.id", primary_key=True)
    player_id: int = Field(foreign_key="user.id", primary_key=True, default=None)
    team_id: Optional[int] = Field(
        default=None,
        foreign_key="matchteam.id",
        index=True,
        nullable=True,
    )

    riot_id: str
    kills: Optional[int] = Field(default=None, nullable=True)
    deaths: Optional[int] = Field(default=None, nullable=True)
    assists: Optional[int] = Field(default=None, nullable=True)
    score: Optional[int] = Field(default=None, nullable=True)
    agent: Optional[str] = Field(default=None, nullable=True)

    user: Optional[User] = Relationship(back_populates="match_players")
    team: Optional[MatchTeam] = Relationship(back_populates="players")
    match: Optional[Match] = Relationship(back_populates="players")  # Add this line
