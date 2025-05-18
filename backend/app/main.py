import json
import asyncio
from fastapi import Response,Request, FastAPI, WebSocket, Depends, APIRouter, HTTPException, Query, status
from typing import Annotated, Literal
from contextlib import asynccontextmanager

from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field
import logging
from .database import init_db, engine
from .schemas import UserRead, UserCreate, MatchPlayerRead, MatchPlayerCreate, MatchCreate, MatchRead, TeamCreate, \
    TeamRead
from sqlmodel import Session, select, SQLModel
from .models import User, Match, MatchPlayer, MatchTeam
from .helper import *
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


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
    limit: int = Field(100, gt=0, le=100)
    order_by: Literal["started_at", "ended_at"] = "started_at"
    tags: list[str] = []


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@router.post("/users/", response_model=UserRead)
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

@router.post("/users/get-or-create", response_model=UserRead)
async def get_or_create(user: UserCreate):
    async with AsyncSession(engine) as session:
        user_db = await get_or_create_user(
            session,
            riot_id=user.riot_id,
            name=user.name,
            tag=user.tag
        )
        return user_db

@router.post("/matches/", response_model=MatchRead)
async def get_or_create(match: MatchCreate):
    async with AsyncSession(engine) as session:
        match_db = await get_or_create_match(
            session, match
        )
        return match_db

@router.post("/matches/", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchCreate):
    async with AsyncSession(engine) as session:
        # 1) Create the Match
        match_db = Match(
            match_uuid=match.match_uuid,
            map_name=match.map_name,
            queue=match.queue,
            started_at=match.started_at,
            ended_at=match.ended_at,
        )
        session.add(match_db)
        await session.commit()
        await session.refresh(match_db)

        return match_db


@router.post("/matches/{match_id}/teams/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(match_id: int, team:TeamCreate):
    async with AsyncSession(engine) as session:
        match = await session.get(Match,match_id)
        if not match:
            raise HTTPException(status_code=404,detail="Match not found")
        team_db = MatchTeam(
            match_id = match_id,
            label = team.label
        )
        session.add(team_db)
        await session.commit()
        await session.refresh(team_db)
        return team_db

@router.post("/matches/{match_id}/teams/{team_id}/players/", response_model=MatchPlayerRead)
async def create_player(match_id:int,team_id:int,player:MatchPlayer):
    async with AsyncSession(engine) as session:
        match = await session.get(Match, match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        team = await session.get(MatchTeam, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        player = MatchPlayer(
            riot_id = player.riot_id,
            kills = player.kills,
            deaths = player.deaths,
            assists = player.assists,
            score = player.score,
            agent = player.agent,
            team_id = team.id
        )

        session.add(player)
        await session.commit()
        await session.refresh(player)
        return player

@router.get("/matches/{match_id}/",response_model=MatchRead)
async def get_match(
        match_id:int
):
    async with AsyncSession(engine) as session:
        match = session.get(Match,match_id)
        if not match:
            raise HTTPException(status_code=404,detail="Match not found")
        return match

@router.get("/matches/", response_model=List[MatchRead])
async def get_matches(
        limit: int = 100,
        order_by: Literal["started_at", "ended_at"] = "started_at"
):
    async with AsyncSession(engine) as session:
        order_col = getattr(Match, order_by)
        statement = select(Match).order_by(order_col).limit(limit)
        result = await session.exec(statement)
        return result.scalars().all()

@router.get("/users/", response_model=list[UserRead])
async def get_users():
    async with AsyncSession(engine) as session:
        statement = select(User)
        result = await session.exec(statement)
        users = result.scalars().all()

        return users

@router.delete(
    "/matches/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a match by its ID"
)
async def delete_match(match_id: int):
    async with AsyncSession(engine) as session:
        # 1) Look up the match
        statement = select(Match).where(Match.id == match_id)
        result = await session.exec(statement)
        match_db = result.scalar_one_or_none()
        if not match_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match with id={match_id} not found"
            )

        # 2) Delete and commit
        await session.delete(match_db)
        await session.commit()

        # 3) Return 204 No Content
        return Response(status_code=status.HTTP_204_NO_CONTENT)


# WS: ingest events
@app.websocket("/live")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = ws.receive()


app.include_router(router)
