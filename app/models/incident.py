from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey
from datetime import datetime, timezone
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True, index=True) # e.g. AER-1042
    type = Column(String(64), nullable=False) # FALL, FIRE, SMOKE, INTRUSION, CROWD, ACCIDENT, SUSPICIOUS
    severity = Column(String(32), default="HIGH") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(32), default="DETECTED", index=True) # DETECTED, VERIFYING, RESPONDING, ARRIVED, RESOLVED, FALSE_ALARM
    confidence = Column(Float, nullable=False) # 0.932
    camera_id = Column(String(64), ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_responder = Column(String(64), ForeignKey("responders.id", ondelete="SET NULL"), nullable=True)
    response_time_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
