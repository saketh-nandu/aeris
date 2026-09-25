from typing import Dict, Any

class EventClassifier:
    """
    Standardizes AI detections into operational incident classifications
    with calibrated severity and dispatch triggers.
    """
    SEVERITY_MAP = {
        "FALL": "HIGH",
        "FIRE": "CRITICAL",
        "SMOKE": "HIGH",
        "INTRUSION": "MEDIUM",
        "CROWD": "MEDIUM",
        "ACCIDENT": "CRITICAL",
        "SUSPICIOUS": "LOW"
    }

    @classmethod
    def classify(cls, detection_type: str, confidence: float, custom_severity: str = None) -> Dict[str, Any]:
        dt = detection_type.upper()
        severity = custom_severity or cls.SEVERITY_MAP.get(dt, "MEDIUM")

        descriptions = {
            "FALL": "Rapid prone descent detected. Subject unresponsive on ground floor.",
            "FIRE": "Active thermal flame anomaly detected. Immediate suppression required.",
            "SMOKE": "Dense vapor expansion observed near ventilation intake.",
            "INTRUSION": "Perimeter breach detected inside restricted zone.",
            "CROWD": "Abnormal crowd concentration exceeding safe threshold.",
            "ACCIDENT": "High-velocity vehicular or transit collision detected.",
            "SUSPICIOUS": "Extensible telemetry anomaly logged for security review."
        }

        return {
            "type": dt,
            "severity": severity,
            "confidence": confidence,
            "description": descriptions.get(dt, f"AI-flagged {dt} event requiring verification."),
            "requires_immediate_dispatch": severity in ["HIGH", "CRITICAL"]
        }

event_classifier = EventClassifier()
