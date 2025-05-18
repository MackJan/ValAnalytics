from fastapi import Response,Request, FastAPI, WebSocket, Depends, APIRouter, HTTPException, Query, status
from typing import Annotated, Literal, Optional
from contextlib import asynccontextmanager
import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field
import logging
from .database import init_db, engine
from .schemas import UserRead, UserCreate, MatchPlayerRead, MatchPlayerCreate, MatchCreate, MatchRead, TeamCreate, \
    TeamRead, TokenData, Token
from sqlmodel import Session, select, SQLModel
from .models import User, Match, MatchPlayer, MatchTeam, UserInDB
from .helper import *
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

#SECRET_KEY = "4d65a1eb33ddc202c4901f066cf0c12cad8f53ec368d053da5bea0e7fa53977c"
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    with AsyncSession(engine) as session:
        user = session.exec((select(User).where(User.username==username)).scalar_one_or_none())
        if user:
            user_dict = session.exec((select(User)).scalars.all())
            return UserInDB(**user_dict)
        return None


def authenticate_user(username: str, password: str):
    with AsyncSession(engine) as session:
        user = session.exec((select(User).where(User.username==username)).scalar_one_or_none())
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user


def create_access_token(data: dict, expires_delta: Optional[timedelta]):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

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
