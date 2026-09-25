import uuid
import logging
from typing import Optional, List, Dict
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.websocket.manager import ws_manager

logger = logging.getLogger("aeris.notifications")

class NotificationService:
    @staticmethod
    async def send_emergency_alert(
        db: Session,
        incident_id: str,
        incident_type: str,
        severity: str,
        location_name: str,
        target_responders: List[Dict]
    ):
        """
        Dispatches emergency push alerts to nearby responder devices 
        via FCM payload and WebSocket push.
        """
        notifications_created = []
        for r in target_responders:
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8].upper()}"
            title = f"🚨 AERIS EMERGENCY: {incident_type} Detected"
            distance_str = f"{int(r['distance_meters'])} m away" if "distance_meters" in r else "Nearby"
            message = f"{distance_str} — {location_name} ({severity} SEVERITY)"
            
            # Persist notification
            notif = Notification(
                id=notif_id,
                user_id=r.get("user_id", r["id"]),
                incident_id=incident_id,
                type="EMERGENCY_NEARBY",
                title=title,
                message=message,
                read=False,
                created_at=datetime.now(timezone.utc)
            )
            db.add(notif)
            notifications_created.append(notif)

            # FCM Payload Mock/Gateway representation
            fcm_payload = {
                "to": r.get("fcm_token", "demo_token"),
                "priority": "high",
                "notification": {
                    "title": title,
                    "body": message,
                    "sound": "emergency_alarm.mp3"
                },
                "data": {
                    "incident_id": incident_id,
                    "type": incident_type,
                    "severity": severity,
                    "location": location_name,
                    "actions": ["VIEW", "RESPOND", "DISMISS"]
                }
            }
            logger.info(f"FCM Payload dispatched for responder {r['id']}: {fcm_payload}")

            # Also push directly to user's personal WebSocket if connected
            await ws_manager.send_personal_message({
                "event": "EMERGENCY_NEARBY",
                "data": {
                    "notification_id": notif_id,
                    "incident_id": incident_id,
                    "type": incident_type,
                    "severity": severity,
                    "location_name": location_name,
                    "distance_meters": r.get("distance_meters", 100),
                    "title": title,
                    "message": message
                }
            }, client_id=r["id"])

        db.commit()
        return notifications_created

notification_service = NotificationService()
