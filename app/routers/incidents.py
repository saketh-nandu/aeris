from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.models.response_event import ResponseEvent
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentAccept,
    IncidentAction,
    ResponseEventSchema
)
from app.services.incident_service import incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentResponse])
def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status.upper())
    if severity:
        query = query.filter(Incident.severity == severity.upper())
    incidents = query.order_by(Incident.created_at.desc()).all()

    # Attach response events
    result = []
    for inc in incidents:
        events = db.query(ResponseEvent).filter(ResponseEvent.incident_id == inc.id).order_by(ResponseEvent.timestamp.asc()).all()
        inc_data = IncidentResponse.model_validate(inc)
        inc_data.events = [ResponseEventSchema.model_validate(e) for e in events]
        result.append(inc_data)
    return result

@router.post("", response_model=IncidentResponse)
async def create_incident(incident_in: IncidentCreate, db: Session = Depends(get_db)):
    incident = await incident_service.create_incident(db, incident_in)
    return incident

@router.get("/{id}", response_model=IncidentResponse)
def get_incident(id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    events = db.query(ResponseEvent).filter(ResponseEvent.incident_id == id).order_by(ResponseEvent.timestamp.asc()).all()
    inc_data = IncidentResponse.model_validate(incident)
    inc_data.events = [ResponseEventSchema.model_validate(e) for e in events]
    return inc_data

@router.post("/{id}/accept", response_model=IncidentResponse)
async def accept_incident(id: str, accept_in: IncidentAccept, db: Session = Depends(get_db)):
    incident = await incident_service.accept_incident(db, id, accept_in.responder_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found or already concluded")
    return incident

@router.post("/{id}/arrive", response_model=IncidentResponse)
async def arrive_incident(id: str, action_in: Optional[IncidentAction] = None, db: Session = Depends(get_db)):
    note = action_in.note if action_in else None
    incident = await incident_service.arrive_incident(db, id, note)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/{id}/resolve", response_model=IncidentResponse)
async def resolve_incident(id: str, action_in: Optional[IncidentAction] = None, db: Session = Depends(get_db)):
    note = action_in.note if action_in else None
    incident = await incident_service.resolve_incident(db, id, note)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.post("/{id}/false-alarm", response_model=IncidentResponse)
async def mark_false_alarm(id: str, action_in: Optional[IncidentAction] = None, db: Session = Depends(get_db)):
    note = action_in.note if action_in else None
    incident = await incident_service.mark_false_alarm(db, id, note)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
