from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime
from datetime import datetime, timezone
from app.database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String(64), primary_key=True, index=True) # e.g. CAM-001, CAM-MOB-0042
    name = Column(String(255), nullable=False)
    type = Column(String(32), default="CCTV") # CCTV, IP, MOBILE
    location_name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(32), default="ONLINE") # ONLINE, OFFLINE, STREAMING
    stream_url = Column(String(512), nullable=True)
    ai_enabled = Column(Boolean, default=True)
    fps = Column(Integer, default=30)
    resolution = Column(String(32), default="1080p")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
