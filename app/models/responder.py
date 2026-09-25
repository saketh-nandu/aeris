from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from app.database import Base

class Responder(Base):
    __tablename__ = "responders"

    id = Column(String(64), primary_key=True, index=True) # e.g. R-0042
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    status = Column(String(32), default="AVAILABLE") # AVAILABLE, BUSY, OFFLINE
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_permission = Column(Boolean, default=True)
    fcm_token = Column(String(512), nullable=True)
    last_location_update = Column(DateTime, default=lambda: datetime.now(timezone.utc))
