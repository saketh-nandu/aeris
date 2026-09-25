from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.responder import ResponderLocationUpdate, ResponderResponse
from app.services.responder_service import responder_service
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/locations", tags=["Location Intelligence"])

@router.post("/update", response_model=ResponderResponse)
async def update_location(loc_in: ResponderLocationUpdate, db: Session = Depends(get_db)):
    resp = responder_service.update_location(
        db, loc_in.responder_id, loc_in.latitude, loc_in.longitude
    )
    if not resp:
        raise HTTPException(status_code=404, detail="Responder not found")

    # Broadcast real-time location ping for live map tracking
    await ws_manager.broadcast("RESPONDER_LOCATION_UPDATED", {
        "responder_id": resp.id,
        "latitude": resp.latitude,
        "longitude": resp.longitude,
        "status": resp.status
    })
    return resp
