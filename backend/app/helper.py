from sqlmodel import Session, select
from .models import User, Match
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import MatchCreate, RiotAuthRequest
import httpx
from fastapi import HTTPException, status

RIOT_AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"


async def riot_login_flow(body: RiotAuthRequest) -> dict:
    async with httpx.AsyncClient(follow_redirects=False) as client:
        # 1) POST to /authorization with the "cookie prep" body
        cookies_payload = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            "scope": "account openid",
        }
        init = await client.post(
            RIOT_AUTH_URL,
            json=cookies_payload,
            headers={"Content-Type": "application/json"}
        )
        if init.status_code not in (200, 204):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Riot cookie setup failed: HTTP {init.status_code}"
            )

        # 2) PUT with the actual credentials + captcha, using the cookies you just got
        resp = await client.put(
            RIOT_AUTH_URL,
            json=body.model_dump(),
            cookies=init.cookies,
            headers={"Content-Type": "application/json"}
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"msg": "Riot auth failed", "error": resp.json()}
            )

        return resp.json()


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
