from fastapi import FastAPI, Request, WebSocket, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

from .database import init_db
from .api import router as api_router
from .websocket import ConnectionManager
import time, logging

logger = logging.getLogger(__name__)

async def lifespan(app: FastAPI):
    await init_db()
    yield

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
    @app.websocket("/ws/agent/{match_id}")
    async def agent_websocket_endpoint(websocket: WebSocket, match_id: str):
        await manager.connect_agent(match_id, websocket)
        try:
            while True:
                data = await websocket.receive_json()
                print(f"Received data from agent for match {match_id}: {data}")
                # Broadcast to all frontend clients watching this match
                await manager.broadcast(match_id, data)

                # Send acknowledgment back to agent
                await websocket.send_text("ACK")
        except WebSocketDisconnect:
            manager.disconnect_agent(match_id)
            print(f"Agent disconnected from match {match_id}")

    @app.websocket("/ws/live/{match_uuid}")
    async def live_ws(ws: WebSocket, match_uuid: str):
        await manager.connect_frontend(match_uuid, ws)
        try:
            await manager.request_data(match_uuid)
            while True:
                await ws.receive_text()  # keep-alive
        except WebSocketDisconnect:
            manager.disconnect_frontend(match_uuid, ws)


    class TriggerRequest(BaseModel):
        match_id: str

    return app
app = create_app()
