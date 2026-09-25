from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from datetime import datetime, timezone
from app.database import Base

class ResponseEvent(Base):
    __tablename__ = "response_events"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    responder_id = Column(String(64), ForeignKey("responders.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(32), nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
