from typing import List, Sequence

from sqlmodel import Session, select
from sqlmodel.sql._expression_select_cls import _T
import json
from .database import engine
from .models import User, Match
import datetime
from sqlalchemy import select
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from .schemas import MatchCreate


async def get_or_create_user(session: AsyncSession, riot_id: str, name: str, tag: str) -> User:
    # 1) Try to find an existing user
    result = await session.exec(select(User).where(User.riot_id == riot_id))
    user_db = result.scalars().one_or_none()
    if user_db:
        return user_db

    # 2) Not found → create
    user_db = User(riot_id=riot_id, name=name, tag=tag)
    session.add(user_db)
    await session.commit()      # persist
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