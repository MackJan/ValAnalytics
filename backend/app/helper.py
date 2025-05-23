from sqlmodel import Session, select
from .models import User, Match, UserAuthentication
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import MatchCreate, UserRiotAuthentication,RiotUser
import requests

async def get_riot_authentication(session: AsyncSession, riot_id: str) -> UserRiotAuthentication:
    """
    Get the Riot authentication information for a user.
    """
    result = await session.exec(select(UserAuthentication).where(UserAuthentication.riot_id == riot_id))
    return result.scalars().one_or_none()

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
