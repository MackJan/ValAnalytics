import json
import asyncio
from fastapi import FastAPI, WebSocket, Depends, APIRouter, HTTPException, Query
from typing import Annotated, Literal
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field

from .database import init_db, engine
from .schemas import UserRead, UserCreate, MatchPlayerRead, MatchPlayerCreate, MatchCreate, MatchRead, TeamCreate, TeamRead
from sqlmodel import Session, select, SQLModel
from .models import Event, User, Match, Round, MatchPlayer, MatchTeam
from .crud import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize the database on startup
    """
    await init_db()
    yield

router = APIRouter(prefix="/api")

app = FastAPI(title="Valorant Performance Tracker", lifespan=lifespan)

class FilterParams(BaseModel):
    limit: int = Field(100,gt=0,le=100)
    order_by: Literal["started_at","ended_at"] = "started_at"
    tags: list[str] = []

@router.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    async with AsyncSession(engine) as session:
        statement = (select(User).where(User.riot_id==user.riot_id))
        us = await session.exec(statement)
        if us:
            raise HTTPException(status_code=409, detail=f"User already exists with id{us.id}")

        # Create a new user instance
        user_db = User(
            riot_id=user.riot_id,
            name=user.name,
            tag=user.tag
        )
        # Add and commit the user to the database
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        return user_db

@router.post("/users/{user_id}/matches/", response_model=list[MatchRead])
async def create_matches(user_id:int, matches: list[MatchCreate]):
    async with AsyncSession(engine) as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        match_instances = []

        for match_data in matches:
            match = Match(
                match_uuid=match_data.match_uuid,
                map_name=match_data.map_name,
                queue=match_data.queue,
                started_at=match_data.started_at,
                ended_at=match_data.ended_at
            )
            session.add(match)
            await session.flush()

            team_red = MatchTeam(match_id=match.id, label="red")
            team_blue = MatchTeam(match_id=match.id, label="blue")
            session.add_all([team_red, team_blue])
            await session.flush()

            team_map = {"red": team_red.id, "blue": team_blue.id}

            for player_data in match_data.match_players:
                match_player = MatchPlayer(
                    match_id=match.id,
                    player_id=player_data.player_id,
                    kills=player_data.kills,
                    deaths=player_data.deaths,
                    assists=player_data.assists,
                    score=player_data.score,
                    agent=player_data.agent,
                    team_id=team_map.get(player_data.team_id)
                )
                session.add(match_player)

            match_instances.append(match)

        await session.commit()

        for match in match_instances:
            await session.refresh(match)
        return match_instances

@router.get("/users/{user_id}/matches/", response_model=list[MatchRead])
async def get_matches(user_id: int,filter_query: Annotated[FilterParams, Query()]):
    async with AsyncSession(engine) as session:
        # Check if the user exists
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="No user found")

        # Query matches for user
        statement = (
            select(Match)
            .where(Match.player_id == user_id)
            .order_by(getattr(Match, filter_query.order_by))
            .limit(filter_query.limit)
        )
        result = await session.exec(statement)
        matches = result.all()

        if not matches:
            raise HTTPException(status_code=404, detail="No matches found")
        return matches

@router.get("/users/", response_model=list[UserRead])
async def get_users():
    async with AsyncSession(engine) as session:
        # Query users
        statement = (
            select(User)
        )
        result = await session.exec(statement)
        users = result.all()

        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return users
# WS: ingest events
@app.websocket("/live")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = ws.receive()



app.include_router(router)