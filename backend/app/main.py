from fastapi import Form, FastAPI, Request, Response, WebSocket, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from typing import List, Literal, Optional, Annotated
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import httpx
import time
import logging

import jwt
from jwt.exceptions import InvalidTokenError

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .database import init_db, engine
from .models import User, Match, MatchPlayer, MatchTeam
from .schemas import (
    UserRead, UserCreate, UserDB, UserRegister, UserProfileUpdate,
    MatchCreate, MatchRead,
    MatchPlayerCreate, MatchPlayerRead,
    TeamCreate, TeamRead,
    Token, TokenData, RiotToken,
    RiotLoginRequest, RiotAuthRequest,
    RiotIdentity,
)
from .helper import get_or_create_user, riot_login_flow

from pydantic import BaseModel, Field
from passlib.context import CryptContext

# Constants
SECRET_KEY = "4d65a1eb33ddc202c4901f066cf0c12cad8f53ec368d053da5bea0e7fa53977c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180


# App setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Valorant Performance Tracker", lifespan=lifespan)

# CORS
origins = ["http://localhost", "http://localhost:8080", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_riot_cookies():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://auth.riotgames.com/authorize")
        cookies = response.cookies
        return cookies


# Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.perf_counter() - start)
    return response


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = str(exc).replace("\n", " ")
    logging.error(f"{request}: {exc_str}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status_code": 10422, "message": exc_str, "data": None},
    )


# Security utils
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Dependencies
async def get_user(session: AsyncSession, username: str) -> Optional[UserDB]:
    result = await session.exec(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    return UserDB.model_validate(user) if user else None


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await get_user(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    async with AsyncSession(engine) as session:
        user = await get_user(session, token_data.username)
        if not user:
            raise credentials_exception
        return user


async def get_current_active_user(
        current_user: Annotated[UserDB, Depends(get_current_user)]
) -> UserDB:
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


# Router
router = APIRouter(prefix="/api")


# Auth Endpoints





@router.post("/riot_login/")
async def riot_login(
        username: str = Form(...),
        password: str = Form(...),
        hcaptcha_token: str = Form(...),
):
    cookies = await get_riot_cookies()

    async with httpx.AsyncClient(cookies=cookies) as client:
        response = await client.post(
            "https://auth.riotgames.com/authorize",
            data={
                "type": "auth",
                "language": "de",
                "remember": True,
                "riot_identity": {
                    "username": username,
                    "password": password,
                    "captcha": hcaptcha_token,
                },
            },
        )
        print(response.headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Login failed")

    # Process the username and password (e.g., authenticate user)
    return {"message": "Login successful"}

@router.post("/auth/riot/")
async def riot_auth(username: str = Form(...),
        password: str = Form(...),
        hcaptcha_token: str = Form(...),):
    """
    Perform Riot Games two-step login:
      1) GET to grab cookies
      2) PUT with { type, language, remember, riot_identity: { captcha, username, password } }
    Returns the full JSON response from Riot (e.g. tokens, session state).
    """
    request = RiotAuthRequest (
        type="auth",
        language="en_US",
        remember=True,
        riot_identity=RiotIdentity(
            captcha=hcaptcha_token,
            username=username,
            password=password
        )
    )
    result = await riot_login_flow(request)
    return {"data": result}

@router.post("/token/", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    async with AsyncSession(engine) as session:
        user = await authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")


# User Endpoints
class UserFilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    order_by: Literal["username"] = "username"
    tags: list[str] = []


@router.post("/users/register", response_model=UserRead)
async def register(user: UserRegister):
    user_db = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    async with AsyncSession(engine) as session:
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
    return user_db


@router.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate):
    hashed = get_password_hash(user.password)
    user_db = User(**user.model_dump(), hashed_password=hashed)
    async with AsyncSession(engine) as session:
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
    return user_db


@router.post("/users/get-or-create", response_model=UserRead)
async def get_or_create_endpoint(user: UserCreate):
    async with AsyncSession(engine) as session:
        return await get_or_create_user(
            session, riot_id=user.riot_id, name=user.name, tag=user.tag
        )


@router.get("/users/", response_model=List[UserRead])
async def list_users():
    async with AsyncSession(engine) as session:
        result = await session.exec(select(User))
    return result.scalars().all()


@router.get("/users/me/", response_model=UserRead)
async def read_users_me(current_user: Annotated[UserDB, Depends(get_current_active_user)]):
    return current_user


@router.patch("/users/me/", response_model=UserRead)
async def update_profile(
        profile: UserProfileUpdate,
        current_user: Annotated[UserDB, Depends(get_current_active_user)]
):
    async with AsyncSession(engine) as session:
        user = await session.get(User, current_user.id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if profile.riot_id and await session.exec(select(User).where(User.riot_id == profile.riot_id)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Riot ID already linked")
        for field, value in profile.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


# Match Endpoints
@router.post("/matches/", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchCreate):
    async with AsyncSession(engine) as session:
        match_db = Match(**match.model_dump())
        session.add(match_db)
        await session.commit()
        await session.refresh(match_db)
    return match_db


@router.get("/matches/", response_model=List[MatchRead])
async def list_matches(
        limit: int = 100,
        order_by: Literal["started_at", "ended_at"] = "started_at"
):
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(Match).order_by(getattr(Match, order_by)).limit(limit)
        )
    return result.scalars().all()


@router.get("/matches/{match_id}/", response_model=MatchRead)
async def get_match(match_id: int):
    async with AsyncSession(engine) as session:
        match = await session.get(Match, match_id)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


@router.delete("/matches/{match_id}/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a match by ID")
async def delete_match(match_id: int):
    async with AsyncSession(engine) as session:
        match = await session.get(Match, match_id)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
        await session.delete(match)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/matches/{match_id}/teams/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(match_id: int, team: TeamCreate):
    async with AsyncSession(engine) as session:
        match = await session.get(Match, match_id)
        if not match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
        team_db = MatchTeam(match_id=match_id, **team.model_dump())
        session.add(team_db)
        await session.commit()
        await session.refresh(team_db)
    return team_db


@router.post("/matches/{match_id}/teams/{team_id}/players/", response_model=MatchPlayerRead)
async def create_player(
        match_id: int,
        team_id: int,
        player: MatchPlayerCreate
):
    async with AsyncSession(engine) as session:
        match = await session.get(Match, match_id)
        team = await session.get(MatchTeam, team_id)
        if not match or not team:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match or Team not found")
        player_db = MatchPlayer(team_id=team_id, **player.model_dump())
        session.add(player_db)
        await session.commit()
        await session.refresh(player_db)
    return player_db


# WebSocket Endpoints
@app.websocket("/live")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        await ws.receive()


# Include router
app.include_router(router)
