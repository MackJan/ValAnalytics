from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List, Annotated, Literal

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .database import get_session, engine
from .schemas import (
    UserRead, UserCreate, UserRegister, UserProfileUpdate,
    MatchRead, MatchCreate, TeamCreate, TeamRead,
    MatchPlayerCreate, MatchPlayerRead,
    RiotUserGet, MatchGet, Token, UserRiotAuthentication, UserNameTag, UserDB,
    ActiveMatchCreate, ActiveMatchRead, ActiveMatchUpdate
)
from .models import User, Match, MatchTeam, MatchPlayer, UserAuthentication, ActiveMatches
from .helper import (
    get_session, get_password_hash, authenticate_user,
    create_access_token, get_current_active_user, get_current_user, get_authentication, ACCESS_TOKEN_EXPIRE_MINUTES
)
from .helper import get_match_history, get_match_history_from_name_tag, get_riot_authentication, get_or_create_user

router = APIRouter()

# --- Auth endpoints ---
# Auth Endpoints
@router.post("/match_history/", response_model=List[MatchGet])
async def get_history(
        player: UserNameTag
):
    async with AsyncSession(engine) as session:
        auth = await get_authentication(session)
        if not auth:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Riot authentication not found for the given riot_id"
            )

        matches = await get_match_history_from_name_tag(player.name, player.tag, auth)
        match_data = []
        print(f"#### {matches}")
        for m in matches["History"]:
            match = MatchGet(
                match_uuid=m["MatchID"],
                game_start_time=m["GameStartTime"],
                queue=m["QueueID"],
            )
            match_data.append(match)

        return match_data


@router.post("/users/riot_user/", response_model=RiotUserGet)
async def get_riot_user(user: RiotUserGet):
    async with AsyncSession(engine) as session:
        res = await get_riot_authentication(session, user.riot_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Riot authentication not found for the given riot_id"
            )

        matches = await get_match_history(session, user.riot_id, res)
        print(matches)
        res = res.model_dump()
        user = RiotUserGet(
            riot_id=res["riot_id"],
        )
        return user


@router.get("/match_hitory/", response_model=List[MatchGet])
async def get_match_history_api(
        riot_id: str,
        auth_id: str,
):
    async with AsyncSession(engine) as session:
        res = await get_riot_authentication(session, auth_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Riot authentication not found for the given riot_id"
            )

        matches = await get_match_history(session, riot_id, res)
        match_data = []
        print(f"#### {matches}")
        for m in matches["History"]:
            match = MatchGet(
                match_uuid=m["MatchID"],
                game_start_time=m["GameStartTime"],
                queue=m["QueueID"],
            )
            match_data.append(match)

        return match_data


@router.post("/users/riot_auth/", response_model=UserRiotAuthentication)
async def riot_auth(auth: UserRiotAuthentication):
    async with AsyncSession(engine) as session:
        auth_db = await session.exec(select(UserAuthentication).where(UserAuthentication.riot_id == auth.riot_id))
        auth_db = auth_db.one_or_none()
        if auth_db:
            setattr(auth_db, "authorization", auth.authorization)
            setattr(auth_db, "entitlement", auth.entitlement)
            setattr(auth_db, "client_platform", auth.client_platform)
            setattr(auth_db, "client_version", auth.client_version)
            setattr(auth_db, "user_agent", auth.user_agent)
            session.add(auth_db)
            await session.commit()
            await session.refresh(auth_db)
            return auth_db

        user_auth = UserAuthentication(
            riot_id=auth.riot_id,
            authorization=auth.authorization,
            entitlement=auth.entitlement,
            client_platform=auth.client_platform,
            client_version=auth.client_version,
            user_agent=auth.user_agent
        )
        session.add(user_auth)
        await session.commit()
        await session.refresh(user_auth)

        return user_auth


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
    return result.all()


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


# Active Match Endpoints
@router.post("/active_matches/", response_model=ActiveMatchRead, status_code=status.HTTP_201_CREATED)
async def create_active_match(active_match: ActiveMatchCreate):
    async with AsyncSession(engine) as session:
        active_match_db = ActiveMatches(**active_match.model_dump())
        session.add(active_match_db)
        await session.commit()
        await session.refresh(active_match_db)
    return active_match_db


@router.get("/active_matches/", response_model=List[ActiveMatchRead])
async def list_active_matches(
        limit: int = 100,
        order_by: Literal["started_at", "ended_at"] = "started_at"
):
    async with AsyncSession(engine) as session:
        result = await session.exec(
            select(ActiveMatches).order_by(getattr(ActiveMatches, order_by)).limit(limit)
        )
    return result.all()


@router.get("/active_matches/{active_match_id}/", response_model=ActiveMatchRead)
async def get_active_match(active_match_id: int):
    async with AsyncSession(engine) as session:
        active_match = await session.get(ActiveMatches, active_match_id)
        if not active_match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active match not found")
    return active_match


@router.patch("/active_matches/{active_match_id}/", response_model=ActiveMatchRead)
async def update_active_match(
        active_match_id: int,
        active_match: ActiveMatchUpdate
):
    async with AsyncSession(engine) as session:
        db_active_match = await session.get(ActiveMatches, active_match_id)
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
        active_match = await session.get(ActiveMatches, active_match_id)
        if not active_match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active match not found")
        await session.delete(active_match)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/active_matches/uuid/{match_uuid}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an active match by UUID")
async def delete_active_match_by_uuid(match_uuid: str):
    async with AsyncSession(engine) as session:
        active_match = await session.exec(
            select(ActiveMatches).where(ActiveMatches.match_uuid == match_uuid)
        )
        active_match = active_match.one_or_none()
        if not active_match:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active match not found")
        await session.delete(active_match)
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
