from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.responder import Responder
from app.services.location_service import location_service
from app.schemas.responder import NearbyResponderResult

class ResponderService:
    @staticmethod
    def get_nearby_responders(
        db: Session,
        incident_lat: float,
        incident_lon: float,
        radius_meters: float = 1000.0,
        limit: int = 5
    ) -> List[NearbyResponderResult]:
        """
        Finds active responders within radius_meters of the incident.
        Filters out:
        - OFFLINE responders
        - BUSY responders
        - Responders with location_permission=False or null coordinates
        Sorts ascending by Haversine distance in meters.
        """
        # Query candidates who are available and have granted location permission
        candidates = db.query(Responder).filter(
            Responder.status == "AVAILABLE",
            Responder.location_permission == True,
            Responder.latitude.isnot(None),
            Responder.longitude.isnot(None)
        ).all()

        results = []
        for r in candidates:
            dist = location_service.haversine_distance(
                incident_lat, incident_lon, r.latitude, r.longitude
            )
            # Only include within geofence radius
            if dist <= radius_meters:
                results.append(NearbyResponderResult(
                    id=r.id,
                    name=r.name,
                    status=r.status,
                    distance_meters=round(dist, 1),
                    latitude=r.latitude,
                    longitude=r.longitude
                ))

        # Sort by proximity
        results.sort(key=lambda x: x.distance_meters)
        return results[:limit]

    @staticmethod
    def update_location(
        db: Session,
        responder_id: str,
        latitude: float,
        longitude: float
    ) -> Optional[Responder]:
        responder = db.query(Responder).filter(Responder.id == responder_id).first()
        if responder:
            responder.latitude = latitude
            responder.longitude = longitude
            responder.last_location_update = datetime.now(timezone.utc)
            db.commit()
            db.refresh(responder)
        return responder

    @staticmethod
    def update_status(
        db: Session,
        responder_id: str,
        status: str
    ) -> Optional[Responder]:
        responder = db.query(Responder).filter(Responder.id == responder_id).first()
        if responder:
            responder.status = status
            db.commit()
            db.refresh(responder)
        return responder

responder_service = ResponderService()
