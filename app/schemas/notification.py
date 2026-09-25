from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    user_id: str
    incident_id: Optional[str] = None
    type: str
    title: str
    message: str

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True
