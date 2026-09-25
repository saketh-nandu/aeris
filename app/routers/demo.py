from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.incident import Incident
from app.models.responder import Responder
from app.models.camera import Camera
from app.schemas.incident import IncidentCreate
from app.services.incident_service import incident_service
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/demo", tags=["System Demo"])

@router.get("/status")
def get_demo_status():
    return {"status": "disabled", "message": "Demo simulation is disabled for live operations."}

@router.post("/trigger-fall")
async def trigger_fall_demo():
    return {"status": "disabled", "message": "Demo simulation is disabled for live operations."}

@router.post("/step/{step_idx}")
async def execute_demo_step(step_idx: int):
    return {"status": "disabled", "step": step_idx, "message": "Demo simulation is disabled for live operations."}

@router.post("/reset")
def reset_demo():
    return {"status": "disabled", "message": "Demo simulation is disabled for live operations."}
