from typing import List, Dict, Any
from app.schemas.camera import CameraResponse
from app.models.detection import Detection
from ai.fall_detection import fall_detector
from ai.fire_detection import fire_smoke_detector
from ai.crowd_detection import crowd_detector
from ai.event_classifier import event_classifier

class AERISDetector:
    """
    Unified AI Detection Engine coordinating Pose, Fall, Fire,
    Intrusion, and Crowd analysis over surveillance video streams.
    """
    def __init__(self):
        self.fall_detector = fall_detector
        self.fire_smoke_detector = fire_smoke_detector
        self.crowd_detector = crowd_detector
        self.classifier = event_classifier

    def analyze_frame_simulation(self, camera_id: str, simulated_event: str = None) -> List[Dict[str, Any]]:
        """
        Generates realistic frame detections for live testing and demonstration.
        """
        detections = []
        if simulated_event == "FALL" or "CAM-002" in camera_id:
            detections.append({
                "camera_id": camera_id,
                "type": "FALL",
                "confidence": 0.932,
                "bounding_box": {"x": 260, "y": 250, "w": 160, "h": 60},
                "severity": "HIGH",
                "metadata": {"pose": "prone", "floor_proximity": 0.94, "duration_s": 8.4}
            })
        elif simulated_event == "SMOKE" or "CAM-004" in camera_id:
            detections.append({
                "camera_id": camera_id,
                "type": "SMOKE",
                "confidence": 0.912,
                "bounding_box": {"x": 480, "y": 110, "w": 180, "h": 160},
                "severity": "HIGH",
                "metadata": {"opacity": 0.72}
            })
        else:
            detections.append({
                "camera_id": camera_id,
                "type": "PERSON",
                "confidence": 0.965,
                "bounding_box": {"x": 220, "y": 140, "w": 70, "h": 160},
                "severity": "LOW",
                "metadata": {"status": "normal_transit"}
            })
        return detections

detector = AERISDetector()
