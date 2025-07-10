from datetime import datetime, timezone

from fastapi import FastAPI, Request, WebSocket, APIRouter
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.websockets import WebSocketDisconnect

from .database import init_db, engine
from .api import router as api_router
from .models import ActiveMatch, ActiveMatchPlayer
from .websocket import ConnectionManager
from .cleanup_service import cleanup_service
import time, logging

logger = logging.getLogger(__name__)

async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    cleanup_service.start()
    logger.info("Application startup complete")

    yield

    # Shutdown
    await cleanup_service.stop()
    logger.info("Application shutdown complete")


async def update_active_match_players(session: AsyncSession, match_id: int, players_data: list):
    """Update or create active match player records"""
    from sqlmodel import delete

    # First, delete existing players for this match to avoid duplicates
    await session.exec(
        delete(ActiveMatchPlayer).where(ActiveMatchPlayer.match_id == match_id)
    )

    # Create new player records
    for player_data in players_data:
        player = ActiveMatchPlayer(
            subject=player_data.get("subject"),
            match_id=match_id,
            character=player_data.get("character"),
            team_id=player_data.get("team_id"),
            game_name=player_data.get("game_name"),
            account_level=player_data.get("account_level"),
            player_card_id=player_data.get("player_card_id"),
            player_title_id=player_data.get("player_title_id"),
            preferred_level_border_id=player_data.get("preferred_level_border_id"),
            agent_icon=player_data.get("agent_icon"),
            rank=player_data.get("rank", "unranked"),
            rr=player_data.get("rr"),
            leaderboard_rank=player_data.get("leaderboard_rank")
        )
        session.add(player)

def update_model_from_json(model_instance, json_data: dict):
    """Update a SQLModel instance with JSON data, only updating valid fields"""
    from datetime import datetime

    model_fields = set(model_instance.__fields__.keys())

    for field, value in json_data.items():
        if field in model_fields and hasattr(model_instance, field):
            # Handle datetime conversion for game_start field
            if field == "game_start" and isinstance(value, (int, float)):
                # Convert milliseconds timestamp to datetime
                value = datetime.fromtimestamp(value / 1000)

            setattr(model_instance, field, value)

    # Always update the last_updated field
    if hasattr(model_instance, 'last_updated'):
        model_instance.last_updated = datetime.now()

    return model_instance

def create_app() -> FastAPI:
    app = FastAPI(title="Valorant Performance Tracker", lifespan=lifespan)
    router = APIRouter()

    manager = ConnectionManager()

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start = time.perf_counter()
        resp = await call_next(request)
        resp.headers["X-Process-Time"] = str(time.perf_counter() - start)
        return resp

    # validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = str(exc).replace("\n", " ")
        logging.error(f"{request}: {exc_str}")
        return JSONResponse(
            status_code=422,
            content={"status_code":10422, "message": exc_str, "data": None},
        )

    # include routers
    app.include_router(api_router, prefix="/api")

    # websocket endpoints
    @app.websocket("/ws/agent/{match_uuid}")
    async def agent_websocket_endpoint(websocket: WebSocket, match_uuid: str):
        await manager.connect_agent(match_uuid, websocket)
        try:
            while True:
                data = await websocket.receive_json()
                print(f"Received data from agent for match {match_uuid}: {data}")

                # update the active match in the database
                async with AsyncSession(engine) as session:
                    result = await session.exec(
                        select(ActiveMatch).where(ActiveMatch.match_uuid == match_uuid)
                    )
                    active_match = result.first()
                    match_data = data.get("data", None)
                    if not match_data:
                        print("No data field found in message")
                        continue

                    # If match_data is a string (JSON), parse it
                    if isinstance(match_data, str):
                        try:
                            import json
                            match_data = json.loads(match_data)
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse match_data JSON: {e}")
                            continue

                    if active_match:
                        # Create a copy to avoid modifying the original
                        match_data_copy = dict(match_data) if isinstance(match_data, dict) else {}

                        # Remove players from match_data before updating main match fields
                        # as players are handled separately via relationships
                        players_data = match_data_copy.pop("players", [])

                        print(f"Updating match with data: {match_data_copy}")
                        print(f"Players data: {len(players_data)} players")

                        # Update main match fields with validation and type conversion
                        update_model_from_json(active_match, match_data_copy)

                        # Handle player data updates
                        if players_data:
                            await update_active_match_players(session, active_match.id, players_data)

                        session.add(active_match)
                        await session.commit()
                        await session.refresh(active_match)
                        print(f"Successfully updated active match {match_uuid}")
                    else:
                        print(f"No active match found for UUID: {match_uuid}")

                # Send the updated data to frontend clients
                await manager.broadcast(match_uuid, data)

                # Send acknowledgment back to agent
                await websocket.send_text("ACK")
        except WebSocketDisconnect:
            manager.disconnect_agent(match_uuid)
            print(f"Agent disconnected from match {match_uuid}")
        except Exception as e:
            print(f"Error in agent websocket: {str(e)}")
            logger.error(f"Error in agent websocket: {str(e)}")

    @app.websocket("/ws/live/{match_uuid}")
    async def live_ws(ws: WebSocket, match_uuid: str):
        await manager.connect_frontend(match_uuid, ws)
        try:
            async with AsyncSession(engine) as session:  # Change to async with
                result =  await session.exec(
                    select(ActiveMatch).where(ActiveMatch.match_uuid == match_uuid)
                )
                active_match = result.first()

                message = {
                    "type": "match_update",
                    "match_uuid": match_uuid,
                    "data": active_match.json(),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

                await manager.broadcast(match_uuid=match_uuid, message=message)
                await ws.receive_text()
        except WebSocketDisconnect:
            manager.disconnect_frontend(match_uuid, ws)


    return app
app = create_app()
