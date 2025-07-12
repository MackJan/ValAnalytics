from fastapi import APIRouter, HTTPException, status, Response
from typing import List
from sqlmodel import select
from .schemas import (
    ActiveMatchCreate, ActiveMatchRead, ActiveMatchUpdate
)
from .models import ActiveMatch
from sqlmodel.ext.asyncio.session import AsyncSession
from .database import engine


router = APIRouter()

# Active Match Endpoints
@router.post("/active_matches/", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_active_match(active_match: ActiveMatchCreate):
    from .models import ActiveMatchPlayer
    from sqlalchemy.orm import selectinload

    async with AsyncSession(engine) as session:
        # Check if a match with this UUID already exists
        existing_match = await session.exec(
            select(ActiveMatch).where(ActiveMatch.match_uuid == active_match.match_uuid)
        )
        existing_match = existing_match.first()

        if existing_match:
            # Delete the existing match (cascade will handle players)
            await session.delete(existing_match)
            await session.commit()

        # Create new active match (exclude players from the main model)
        match_data = active_match.model_dump(exclude={'players'})
        active_match_db = ActiveMatch(**match_data)
        session.add(active_match_db)
        await session.commit()  # Use commit instead of flush to ensure ID is available
        await session.refresh(active_match_db)

        # Create players if provided
        if active_match.players:
            for player_data in active_match.players:
                player = ActiveMatchPlayer(
                    subject=player_data.subject,
                    match_id=active_match_db.id,
                    character=player_data.character,
                    team_id=player_data.team_id,
                    game_name=player_data.game_name,
                    account_level=player_data.account_level,
                    player_card_id=player_data.player_card_id,
                    player_title_id=player_data.player_title_id,
                    preferred_level_border_id=player_data.preferred_level_border_id,
                    agent_icon=player_data.agent_icon,
                    rank=player_data.rank,
                    rr=player_data.rr,
                    leaderboard_rank=player_data.leaderboard_rank
                )
                session.add(player)

            await session.commit()


@router.get("/active_matches/", response_model=List[ActiveMatchRead])
async def list_active_matches(
        limit: int = 100,
):
    async with AsyncSession(engine) as session:
        # Use selectinload to eagerly load the players relationship
        from sqlmodel import select
        from sqlalchemy.orm import selectinload

        result = await session.exec(
            select(ActiveMatch)
            .options(selectinload(ActiveMatch.players))
            .order_by(getattr(ActiveMatch, 'last_updated').desc())
            .limit(limit)
        )
        active_matches = result.all()

        # Convert to list to ensure we have the data before session closes
        return list(active_matches)


@router.get("/active_matches/{active_match_id}/", response_model=ActiveMatchRead)
async def get_active_match(active_match_id: int):
    async with AsyncSession(engine) as session:
        from sqlalchemy.orm import selectinload

        # Use selectinload to eagerly load the players relationship
        result = await session.exec(
            select(ActiveMatch)
            .options(selectinload(ActiveMatch.players))
            .where(ActiveMatch.id == active_match_id)
        )
        active_match = result.first()

        if not active_match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active match not found")
    return active_match


@router.patch("/active_matches/{active_match_id}/", response_model=ActiveMatchRead)
async def update_active_match(
        active_match_id: int,
        active_match: ActiveMatchUpdate
):
    async with AsyncSession(engine) as session:
        db_active_match = await session.get(ActiveMatch, active_match_id)
        if not db_active_match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active match not found")
        for field, value in active_match.model_dump(exclude_unset=True).items():
            setattr(db_active_match, field, value)
        session.add(db_active_match)
        await session.commit()
        await session.refresh(db_active_match)
    return db_active_match


@router.delete("/active_matches/{active_match_id}/", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an active match by ID")
async def delete_active_match(active_match_id: int):
    async with AsyncSession(engine) as session:
        active_match = await session.get(ActiveMatch, active_match_id)
        if not active_match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active match not found")
        await session.delete(active_match)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/active_matches/uuid/{match_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an active match by UUID")
async def delete_active_match_by_uuid(match_id: str):
    async with AsyncSession(engine) as session:
        active_match = await session.exec(
            select(ActiveMatch).where(ActiveMatch.match_uuid == match_id)
        )
        active_match = active_match.one_or_none()
        if not active_match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active match not found")
        await session.delete(active_match)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
