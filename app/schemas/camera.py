from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CameraBase(BaseModel):
    name: str
    type: str = "CCTV"
    location_name: str
    latitude: float
    longitude: float
    status: str = "ONLINE"
    stream_url: Optional[str] = None
    ai_enabled: bool = True
    fps: int = 30
    resolution: str = "1080p"

class CameraCreate(CameraBase):
    id: Optional[str] = None

class CameraResponse(CameraBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class CameraPairRequest(BaseModel):
    token: str
    device_name: str = "Android mobile camera"
    latitude: float
    longitude: float

class PairingSessionResponse(BaseModel):
    token: str
    qr_image_url: str
    expires_at: datetime

class PairingStatusResponse(BaseModel):
    status: str
    camera: Optional[CameraResponse] = None
