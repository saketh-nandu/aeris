import uuid
import logging
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.response_event import ResponseEvent
from app.models.responder import Responder
from app.schemas.incident import IncidentCreate
from app.services.responder_service import responder_service
from app.services.notification_service import notification_service
from app.websocket.manager import ws_manager

logger = logging.getLogger("aeris.incidents")

class IncidentService:
    @staticmethod
    async def create_incident(db: Session, incident_in: IncidentCreate) -> Incident:
        incident_id = incident_in.id or f"AER-{uuid.uuid4().hex[:4].upper()}"
        now = datetime.now(timezone.utc)
        
        incident = Incident(
            id=incident_id,
            type=incident_in.type.upper(),
            severity=incident_in.severity.upper(),
            status="DETECTED",
            confidence=incident_in.confidence,
            camera_id=incident_in.camera_id,
            latitude=incident_in.latitude,
            longitude=incident_in.longitude,
            location_name=incident_in.location_name,
            description=incident_in.description,
            created_at=now
        )
        db.add(incident)
        
        # Log DETECTED response event
        evt = ResponseEvent(
            id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            status="DETECTED",
            note=f"AI confirmed {incident_in.type} anomaly with {incident_in.confidence*100:.1f}% confidence on {incident_in.camera_id or 'source'}",
            timestamp=now
        )
        db.add(evt)
        db.commit()
        db.refresh(incident)

        # Broadcast INCIDENT_CREATED to all connected command centers & responders
        await ws_manager.broadcast("INCIDENT_CREATED", {
            "incident_id": incident.id,
            "type": incident.type,
            "severity": incident.severity,
            "status": incident.status,
            "confidence": incident.confidence,
            "camera_id": incident.camera_id,
            "location_name": incident.location_name,
            "latitude": incident.latitude,
            "longitude": incident.longitude,
            "description": incident.description,
            "timestamp": now.isoformat()
        })

        # Find nearby available responders
        nearby = responder_service.get_nearby_responders(
            db, incident.latitude, incident.longitude, radius_meters=1500.0, limit=5
        )
        if nearby:
            target_list = [
                {
                    "id": r.id,
                    "name": r.name,
                    "distance_meters": r.distance_meters,
                    "fcm_token": f"token_{r.id}"
                }
                for r in nearby
            ]
            await notification_service.send_emergency_alert(
                db, incident.id, incident.type, incident.severity, incident.location_name, target_list
            )
            # Log DISPATCHED event
            disp_evt = ResponseEvent(
                id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
                incident_id=incident_id,
                status="DISPATCHED",
                note=f"Dispatched push notifications to {len(nearby)} nearby responders (Nearest: {nearby[0].name} at {int(nearby[0].distance_meters)}m)",
                timestamp=datetime.now(timezone.utc)
            )
            db.add(disp_evt)
            db.commit()

        return incident

    @staticmethod
    async def accept_incident(db: Session, incident_id: str, responder_id: str) -> Optional[Incident]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident or incident.status in ["RESOLVED", "FALSE_ALARM"]:
            return incident

        now = datetime.now(timezone.utc)
        incident.status = "RESPONDING"
        incident.assigned_responder = responder_id
        
        # Mark responder as BUSY
        responder = db.query(Responder).filter(Responder.id == responder_id).first()
        responder_name = responder.name if responder else responder_id
        if responder:
            responder.status = "BUSY"

        evt = ResponseEvent(
            id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            responder_id=responder_id,
            status="RESPONDING",
            note=f"Responder {responder_name} ({responder_id}) accepted dispatch",
            timestamp=now
        )
        db.add(evt)
        db.commit()
        db.refresh(incident)

        await ws_manager.broadcast("RESPONDER_ACCEPTED", {
            "incident_id": incident.id,
            "responder_id": responder_id,
            "responder_name": responder_name,
            "status": "RESPONDING",
            "timestamp": now.isoformat()
        })
        return incident

    @staticmethod
    async def arrive_incident(db: Session, incident_id: str, note: Optional[str] = None) -> Optional[Incident]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        now = datetime.now(timezone.utc)
        incident.status = "ARRIVED"

        evt = ResponseEvent(
            id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            responder_id=incident.assigned_responder,
            status="ARRIVED",
            note=note or f"Responder checked in on scene at {incident.location_name}",
            timestamp=now
        )
        db.add(evt)
        db.commit()
        db.refresh(incident)

        await ws_manager.broadcast("RESPONDER_ARRIVED", {
            "incident_id": incident.id,
            "responder_id": incident.assigned_responder,
            "status": "ARRIVED",
            "timestamp": now.isoformat()
        })
        return incident

    @staticmethod
    async def resolve_incident(db: Session, incident_id: str, note: Optional[str] = None) -> Optional[Incident]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        now = datetime.now(timezone.utc)
        incident.status = "RESOLVED"
        incident.resolved_at = now
        
        # Calculate response time
        if incident.created_at:
            delta = now - incident.created_at.replace(tzinfo=timezone.utc) if incident.created_at.tzinfo is None else now - incident.created_at
            incident.response_time_seconds = max(1, int(delta.total_seconds()))

        # Free the assigned responder back to AVAILABLE
        if incident.assigned_responder:
            resp = db.query(Responder).filter(Responder.id == incident.assigned_responder).first()
            if resp:
                resp.status = "AVAILABLE"

        evt = ResponseEvent(
            id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            responder_id=incident.assigned_responder,
            status="RESOLVED",
            note=note or f"Emergency neutralized and subject assisted. Total response time: {incident.response_time_seconds}s",
            timestamp=now
        )
        db.add(evt)
        db.commit()
        db.refresh(incident)

        formatted_time = f"{incident.response_time_seconds // 60:02d}:{incident.response_time_seconds % 60:02d}"
        await ws_manager.broadcast("INCIDENT_RESOLVED", {
            "incident_id": incident.id,
            "status": "RESOLVED",
            "response_time_seconds": incident.response_time_seconds,
            "formatted_response_time": formatted_time,
            "timestamp": now.isoformat()
        })
        return incident

    @staticmethod
    async def mark_false_alarm(db: Session, incident_id: str, note: Optional[str] = None) -> Optional[Incident]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        now = datetime.now(timezone.utc)
        incident.status = "FALSE_ALARM"
        incident.resolved_at = now

        if incident.assigned_responder:
            resp = db.query(Responder).filter(Responder.id == incident.assigned_responder).first()
            if resp:
                resp.status = "AVAILABLE"

        evt = ResponseEvent(
            id=f"EVT-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            responder_id=incident.assigned_responder,
            status="FALSE_ALARM",
            note=note or "Incident marked as false alarm by Command Center operator",
            timestamp=now
        )
        db.add(evt)
        db.commit()
        db.refresh(incident)

        await ws_manager.broadcast("INCIDENT_FALSE_ALARM", {
            "incident_id": incident.id,
            "status": "FALSE_ALARM",
            "timestamp": now.isoformat()
        })
        return incident

incident_service = IncidentService()
