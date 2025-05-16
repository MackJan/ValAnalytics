import json
import asyncio
from fastapi import Request, FastAPI, WebSocket, Depends, APIRouter, HTTPException, Query, status
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
from .crud import *
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

@router.post(
    "/matches/bulk/",
    response_model=List[MatchRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple matches in one request",
)
async def create_matches_bulk(matches: List[MatchCreate]):
    created_matches: List[Match] = []

    async with AsyncSession(engine) as session:
        # Use a transaction: either all match creations succeed or fail
        async with session.begin():
            for m in matches:
                # 1) Create the Match row
                match_db = Match(
                    match_uuid=m.match_uuid,
                    map_name=m.map_name,
                    queue=m.queue,
                    started_at=m.started_at,
                    ended_at=m.ended_at,
                )
                session.add(match_db)
                # Flush so match_db.id is populated before we create its players
                await session.flush()

                # 2) Attach players if provided
                if m.match_players:
                    for p in m.match_players:
                        # look up the User by riot_id
                        result = await session.exec(
                            select(User).where(User.riot_id == p.riot_id)
                        )
                        user_db = result.one_or_none()
                        if not user_db:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with riot_id '{p.riot_id}' not found",
                            )

                        mp = MatchPlayer(
                            match_id=match_db.id,
                            player_id=user_db.id,
                            riot_id=p.riot_id,
                            kills=p.kills,
                            deaths=p.deaths,
                            assists=p.assists,
                            score=p.score,
                            agent=p.agent,
                            team_id=p.team_id,
                        )
                        session.add(mp)

                # Collect for response
                created_matches.append(match_db)

        # at this point, the transaction has been committed
        # refresh each so that any defaults (or relationships, if you choose) are populated
        for match_db in created_matches:
            await session.refresh(match_db)

    return created_matches

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

        # 2) Optional: attach players
        if match.match_players:
            for p in match.match_players:
                # find the User by riot_id
                result = await session.exec(select(User).where(User.riot_id == p.riot_id))
                user_db = result.one_or_none()
                if not user_db:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User with riot_id '{p.riot_id}' not found"
                    )
                mp = MatchPlayer(
                    match_id=match_db.id,
                    player_id=user_db.id,
                    riot_id=p.riot_id,
                    kills=p.kills,
                    deaths=p.deaths,
                    assists=p.assists,
                    score=p.score,
                    agent=p.agent,
                    team_id=p.team_id,
                )
                session.add(mp)
            await session.commit()
            # no need to refresh match_db itself here since MatchRead doesn’t include players

        return match_db


@router.get("/matches/", response_model=List[MatchRead])
async def get_matches(
        limit: int = 100,
        order_by: Literal["started_at", "ended_at"] = "started_at"
):
    async with AsyncSession(engine) as session:
        order_col = getattr(Match, order_by)
        statement = select(Match).order_by(order_col).limit(limit)
        result = await session.exec(statement)
        return result.all()


@router.get("/matches/{match_id}", response_model=MatchRead)
async def get_match(match_id: int):
    async with AsyncSession(engine) as session:
        statement = select(Match).where(Match.id == match_id)
        result = await session.exec(statement)
        match_db = result.one_or_none()
        if not match_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )
        return match_db


@router.get("/users/", response_model=list[UserRead])
async def get_users():
    async with AsyncSession(engine) as session:
        statement = select(User)
        result = await session.exec(statement)
        users = result.all()

        return users


# WS: ingest events
@app.websocket("/live")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = ws.receive()


app.include_router(router)
