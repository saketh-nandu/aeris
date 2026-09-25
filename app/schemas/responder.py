from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ResponderBase(BaseModel):
    name: str
    status: str = "AVAILABLE" # AVAILABLE, BUSY, OFFLINE
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_permission: bool = True
    fcm_token: Optional[str] = None

class ResponderCreate(ResponderBase):
    id: Optional[str] = None
    user_id: Optional[str] = None

class ResponderResponse(ResponderBase):
    id: str
    user_id: Optional[str] = None
    last_location_update: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResponderLocationUpdate(BaseModel):
    responder_id: str
    latitude: float
    longitude: float

class ResponderStatusUpdate(BaseModel):
    responder_id: str
    status: str # AVAILABLE, BUSY, OFFLINE

class NearbyResponderResult(BaseModel):
    id: str
    name: str
    status: str
    distance_meters: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
