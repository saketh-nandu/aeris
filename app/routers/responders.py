from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.responder import Responder
from app.schemas.responder import (
    ResponderResponse,
    ResponderStatusUpdate,
    NearbyResponderResult
)
from app.services.responder_service import responder_service
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/responders", tags=["Responders"])

@router.get("", response_model=List[ResponderResponse])
def get_responders(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Responder)
    if status:
        query = query.filter(Responder.status == status.upper())
    return query.all()

@router.get("/nearby", response_model=List[NearbyResponderResult])
def get_nearby(
    latitude: float = Query(..., description="Target incident latitude"),
    longitude: float = Query(..., description="Target incident longitude"),
    radius_meters: float = Query(1500.0, description="Search radius in meters"),
    limit: int = Query(5, description="Max responders to return"),
    db: Session = Depends(get_db)
):
    return responder_service.get_nearby_responders(db, latitude, longitude, radius_meters, limit)

@router.post("/status", response_model=ResponderResponse)
async def update_status(status_in: ResponderStatusUpdate, db: Session = Depends(get_db)):
    resp = responder_service.update_status(db, status_in.responder_id, status_in.status.upper())
    if not resp:
        raise HTTPException(status_code=404, detail="Responder not found")
    
    await ws_manager.broadcast("RESPONDER_STATUS_CHANGED", {
        "responder_id": resp.id,
        "name": resp.name,
        "status": resp.status
    })
    return resp
