import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
import app.models
from app.routers import auth_router, cameras_router, incidents_router, responders_router, locations_router, notifications_router
from app.websocket.manager import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aeris.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Empty by design: operational records are never fabricated at startup.
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.PROJECT_NAME, version="2.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
for router in (auth_router, cameras_router, incidents_router, responders_router, locations_router, notifications_router):
    app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ONLINE", "service": "AERIS Backend", "backend": "CONNECTED", "ai_engine": "ONLINE", "realtime": "CONNECTED", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        await websocket.send_json({"event": "CONNECTED", "client_id": client_id, "status": "ONLINE"})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, client_id)
    except Exception as exc:
        logger.warning("WebSocket error for %s: %s", client_id, exc)
        ws_manager.disconnect(websocket, client_id)
