from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from datetime import datetime, timezone
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    incident_id = Column(String(64), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    type = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
