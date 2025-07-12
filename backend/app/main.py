from datetime import datetime, timezone

from fastapi import FastAPI, Request, WebSocket, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.websockets import WebSocketDisconnect

from .database import init_db, engine
from .api import router as api_router
from .models import ActiveMatch
from .websocket import ConnectionManager
import time, logging
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    #cleanup_service.start()
    logger.info("Application startup complete")

    yield

    # Shutdown
    #await cleanup_service.stop()
    logger.info("Application shutdown complete")


def update_model_from_json(model_instance, json_data: dict):
    """Update a SQLModel instance with JSON data, only updating valid fields"""
    from datetime import datetime, timezone

    # Use model_fields for Pydantic v2 compatibility
    model_fields = set(model_instance.model_fields.keys())

    for field, value in json_data.items():
        if field in model_fields and hasattr(model_instance, field):
            # Handle datetime conversion for game_start field
            if field == "game_start" and isinstance(value, (int, float)):
                # Check if timestamp is in milliseconds (> year 2001 in seconds)
                if value > 1000000000000:  # milliseconds timestamp
                    value = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
                else:  # seconds timestamp
                    value = datetime.fromtimestamp(value, tz=timezone.utc)

                # Convert to timezone-naive datetime for PostgreSQL
                value = value.replace(tzinfo=None)

            setattr(model_instance, field, value)

    # Always update the last_updated field (timezone-naive)
    if hasattr(model_instance, 'last_updated'):
        model_instance.last_updated = datetime.now(timezone.utc).replace(tzinfo=None)

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

                        # Remove players from match_data since they don't change after initial creation
                        match_data_copy.pop("players", [])

                        print(f"Updating match with data: {match_data_copy}")

                        # Update main match fields with validation and type conversion
                        update_model_from_json(active_match, match_data_copy)

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
            # Send initial match data when frontend connects
            async with AsyncSession(engine) as session:
                result = await session.exec(
                    select(ActiveMatch).where(ActiveMatch.match_uuid == match_uuid).options(selectinload(ActiveMatch.players))
                )
                active_match = result.first()

                if active_match:
                    # Convert the SQLModel to dict manually to avoid serialization issues
                    match_dict = {
                        "id": active_match.id,
                        "match_uuid": active_match.match_uuid,
                        "created_at": active_match.created_at.isoformat() if active_match.created_at else None,
                        "ended_at": active_match.ended_at.isoformat() if active_match.ended_at else None,
                        "last_updated": active_match.last_updated.isoformat() if active_match.last_updated else None,
                        "game_map": active_match.game_map,
                        "game_start": active_match.game_start.isoformat() if active_match.game_start else None,
                        "game_mode": active_match.game_mode,
                        "state": active_match.state,
                        "party_owner_score": active_match.party_owner_score,
                        "party_owner_enemy_score": active_match.party_owner_enemy_score,
                        "party_size": active_match.party_size,
                        "players": []
                    }

                    # Add player data if available
                    if active_match.players:
                        for player in active_match.players:
                            player_dict = {
                                "subject": player.subject,
                                "match_id": player.match_id,
                                "character": player.character,
                                "team_id": player.team_id,
                                "game_name": player.game_name,
                                "account_level": player.account_level,
                                "player_card_id": player.player_card_id,
                                "player_title_id": player.player_title_id,
                                "preferred_level_border_id": player.preferred_level_border_id,
                                "agent_icon": player.agent_icon,
                                "rank": player.rank,
                                "rr": player.rr,
                                "leaderboard_rank": player.leaderboard_rank
                            }
                            match_dict["players"].append(player_dict)

                    message = {
                        "type": "match_update",
                        "match_uuid": match_uuid,
                        "data": match_dict,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }

                    await ws.send_json(message)
                    print(f"Sent initial match data to frontend for {match_uuid}")
                else:
                    # Request data from agent if no match found
                    #await manager.request_data(match_uuid)
                    print(f"Requested data from agent for {match_uuid}")

            # Keep connection alive and wait for disconnect
            while True:
                try:
                    await ws.receive_text()
                except WebSocketDisconnect:
                    break
        except WebSocketDisconnect:
            manager.disconnect_frontend(match_uuid, ws)
            print(f"Frontend disconnected from match {match_uuid}")
        except Exception as e:
            print(f"Error in live websocket: {str(e)}")
            logger.error(f"Error in live websocket: {str(e)}")

    return app
app = create_app()
