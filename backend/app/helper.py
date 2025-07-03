import json, jwt, time
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .models import User, UserAuthentication, Match
from .schemas import TokenData, RiotUserGet, UserNameTag, MatchGet, UserRiotAuthentication, RiotUser, MatchCreate
from .database import engine, get_session


riot_api = "RGAPI-9db13490-153b-4787-ba20-b4285ce3fde3"

# ---- Security constants ----
SECRET_KEY = "4d65a1eb33ddc202c4901f066cf0c12cad8f53ec368d053da5bea0e7fa53977c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ---- DB/dependency helpers ----

async def get_user(session: AsyncSession, username: str):
    result = await session.exec(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    return user

async def authenticate_user(session: AsyncSession, username: str, password: str):
    user = await get_user(session, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException( status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    async with get_session() as session:
        user = await get_user(session, username)
        if not user:
            raise credentials_exception
        return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

async def get_authentication(session: AsyncSession) -> UserAuthentication:
    """
    Get the authentication information for a user.
    """
    result = await session.exec(
        select(UserAuthentication).order_by(UserAuthentication.num_used.asc())
    )
    return result.scalars().first()


async def get_riot_authentication(session: AsyncSession, riot_id: str) -> UserRiotAuthentication:
    """
    Get the Riot authentication information for a user.
    """
    result = await session.exec(select(UserAuthentication).where(UserAuthentication.riot_id == riot_id))
    return result.scalars().one_or_none()


async def get_match_history_from_name_tag(name: str, tag: str, auth: UserRiotAuthentication) -> RiotUser:
    """
    Get the Riot user information for a user.
    """
    print(f"Fetching match history for {name}#{tag}")
    res = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={riot_api}")

    if res.status_code != 200:
        raise Exception(f"Error fetching user data: {res.status_code} - {res.text}")

    riot_id = res.json().get("puuid")

    auth_data = auth.model_dump()

    headers = {
        'Authorization': auth_data['authorization'],
        'X-Riot-Entitlements-JWT': auth_data['entitlement'],
        'X-Riot-ClientPlatform': auth_data['client_platform'],
        'X-Riot-ClientVersion': auth_data['client_version'],
        "User-Agent": auth_data['user_agent'],
    }
    print(riot_id)
    print(f"#### Headers: {headers}")
    response = requests.get(f"https://pd.eu.a.pvp.net/match-history/v1/history/{riot_id}", headers=headers)

    return response.json()


async def get_match_history(session: AsyncSession, riot_id: str, auth: UserRiotAuthentication) -> RiotUser:
    """
    Get the Riot user information for a user.
    """
    auth_data = auth.model_dump()

    headers = {
        'Authorization': auth_data['authorization'],
        'X-Riot-Entitlements-JWT': auth_data['entitlement'],
        'X-Riot-ClientPlatform': auth_data['client_platform'],
        'X-Riot-ClientVersion': auth_data['client_version'],
        "User-Agent": auth_data['user_agent'],
    }
    response = requests.get(f"https://pd.eu.a.pvp.net/match-history/v1/history/{riot_id}", headers=headers)

    return response.json()


async def get_or_create_user(session: AsyncSession, riot_id: str, name: str, tag: str) -> User:
    # 1) Try to find an existing user
    result = await session.exec(select(User).where(User.riot_id == riot_id))
    user_db = result.scalars().one_or_none()
    if user_db:
        return user_db

    # 2) Not found → create
    user_db = User(riot_id=riot_id, name=name, tag=tag)
    session.add(user_db)
    await session.commit()  # persist
    await session.refresh(user_db)  # populate user_db.id, created_at, etc.
    return user_db


async def get_or_create_match(session: AsyncSession, match: MatchCreate):
    result = await session.exec(select(Match).where(Match.match_uuid == match.match_uuid))
    match_db = result.scalars().one_or_none()
    if match_db:
        return match_db

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
