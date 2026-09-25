from typing import Dict, Any, List, Optional

class CrowdDetector:
    """
    Evaluates localized person count and density per zone.
    Triggers CROWD alerts when density exceeds safety thresholds.
    """
    def __init__(self, crowd_limit: int = 10, panic_dispersion_threshold: float = 4.0):
        self.crowd_limit = crowd_limit
        self.panic_dispersion = panic_dispersion_threshold

    def evaluate_zone_density(self, zone_name: str, detected_people: List[dict]) -> Optional[Dict[str, Any]]:
        count = len(detected_people)
        if count >= self.crowd_limit:
            severity = "CRITICAL" if count >= self.crowd_limit * 1.8 else "MEDIUM"
            confidence = min(0.96, 0.70 + (count / 30.0))
            return {
                "event_type": "CROWD",
                "severity": severity,
                "confidence": round(confidence, 3),
                "person_count": count,
                "zone": zone_name
            }
        return None

crowd_detector = CrowdDetector()
