import json
import asyncio
from fastapi import FastAPI, WebSocket, Depends, APIRouter, HTTPException, Query
from typing import Annotated, Literal
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field

from .database import init_db, engine
from .schemas import EventCreate, MatchRead, EventRead, UserCreate
from sqlmodel import Session, select
from .models import Event, User, Match, Round


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
async def create_matches(user_id:int, matches: list[MatchRead]):
    async with AsyncSession(engine) as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        match_instances = {
            Match(
                match_uuid=match.match_uuid,
                map_name=match.map_name,
                agent=match.agent,
                started_at=match.started_at,
                ended_at=match.ended_at,
                player_id=user_id
            )
            for match in matches
        }

        session.add_all(match_instances)
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

# WS: ingest events
@app.websocket("/live")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = ws.receive()

app.include_router(router)