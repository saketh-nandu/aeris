from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from datetime import datetime, timezone
from app.database import Base

class Detection(Base):
    __tablename__ = "detections"

    id = Column(String(64), primary_key=True, index=True)
    camera_id = Column(String(64), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(64), nullable=False)
    confidence = Column(Float, nullable=False)
    bounding_box = Column(Text, nullable=True) # JSON string representation
    severity = Column(String(32), default="HIGH")
    snapshot_url = Column(String(512), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
