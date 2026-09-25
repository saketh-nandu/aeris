from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class IncidentBase(BaseModel):
    type: str # FALL, FIRE, SMOKE, INTRUSION, CROWD, ACCIDENT, SUSPICIOUS
    severity: str = "HIGH" # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float # e.g. 0.932
    camera_id: Optional[str] = None
    latitude: float
    longitude: float
    location_name: str
    description: Optional[str] = None

class IncidentCreate(IncidentBase):
    id: Optional[str] = None

class ResponseEventSchema(BaseModel):
    id: str
    incident_id: str
    responder_id: Optional[str] = None
    status: str
    note: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class IncidentResponse(IncidentBase):
    id: str
    status: str # DETECTED, VERIFYING, RESPONDING, ARRIVED, RESOLVED, FALSE_ALARM
    assigned_responder: Optional[str] = None
    response_time_seconds: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    events: Optional[List[ResponseEventSchema]] = None

    class Config:
        from_attributes = True

class IncidentAccept(BaseModel):
    responder_id: str

class IncidentAction(BaseModel):
    note: Optional[str] = None
