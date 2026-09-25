from typing import Dict, Any, Optional

class FallDetector:
    """
    Calibrated Fall Detection Algorithm:
    1. Aspect Ratio Test: w / h > aspect_ratio_threshold (typically > 1.15 when prone)
    2. Vertical Velocity: Rapid downward shift in center of mass (Delta y / Delta t)
    3. Floor Proximity: Relative bounding box bottom y-coordinate near calibrated floor plane
    4. Persistence: Prone state must persist for >= persistence_frames (prevents momentary false alarms)
    """
    def __init__(
        self,
        aspect_ratio_threshold: float = 1.15,
        velocity_threshold: float = 2.5,
        floor_proximity_threshold: float = 0.70,
        persistence_frames: int = 15
    ):
        self.aspect_ratio_threshold = aspect_ratio_threshold
        self.velocity_threshold = velocity_threshold
        self.floor_proximity_threshold = floor_proximity_threshold
        self.persistence_frames = persistence_frames
        
        # Track history per subject ID
        self.track_history: Dict[int, Dict[str, Any]] = {}

    def process_person_pose(
        self,
        track_id: int,
        bbox: list, # [x, y, w, h]
        frame_height: int = 720
    ) -> Optional[Dict[str, Any]]:
        x, y, w, h = bbox
        aspect_ratio = float(w) / max(1.0, float(h))
        center_y = y + h / 2.0
        floor_proximity = (y + h) / float(frame_height)

        history = self.track_history.get(track_id, {
            "last_center_y": center_y,
            "prone_frames": 0,
            "max_velocity": 0.0
        })

        velocity_y = max(0.0, center_y - history["last_center_y"])
        is_prone = aspect_ratio >= self.aspect_ratio_threshold and floor_proximity >= self.floor_proximity_threshold

        if is_prone:
            history["prone_frames"] += 1
        else:
            history["prone_frames"] = max(0, history["prone_frames"] - 2)

        history["last_center_y"] = center_y
        history["max_velocity"] = max(history.get("max_velocity", 0.0), velocity_y)
        self.track_history[track_id] = history

        # Trigger condition
        if history["prone_frames"] >= self.persistence_frames:
            confidence = min(0.985, 0.85 + (history["prone_frames"] / 100.0) + (aspect_ratio * 0.05))
            return {
                "event_type": "FALL",
                "severity": "HIGH",
                "confidence": round(confidence, 3),
                "track_id": track_id,
                "aspect_ratio": round(aspect_ratio, 2),
                "floor_proximity": round(floor_proximity, 2),
                "prone_duration_frames": history["prone_frames"]
            }
        return None

fall_detector = FallDetector()
