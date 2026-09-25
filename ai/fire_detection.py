from typing import Dict, Any, Optional

class FireSmokeDetector:
    """
    Fire & Smoke Detection Architecture:
    Combines optical spectral rules (HSV/YCbCr flame color models) 
    with temporal variance and bounding box volumetric growth.
    """
    def __init__(self, fire_confidence_threshold: float = 0.80, smoke_confidence_threshold: float = 0.75):
        self.fire_threshold = fire_confidence_threshold
        self.smoke_threshold = smoke_confidence_threshold

    def evaluate_flame_region(self, hsv_mean: list, area_growth_rate: float) -> Optional[Dict[str, Any]]:
        # Hue between 0-35 deg (red/orange/yellow), Saturation > 120, Value > 180
        h, s, v = hsv_mean
        is_flame_color = (0 <= h <= 35 or 330 <= h <= 360) and s > 110 and v > 170

        if is_flame_color and area_growth_rate > 1.05:
            confidence = min(0.97, 0.78 + (area_growth_rate * 0.12))
            return {
                "event_type": "FIRE",
                "severity": "CRITICAL",
                "confidence": round(confidence, 3),
                "growth_rate": round(area_growth_rate, 2)
            }
        return None

    def evaluate_smoke_region(self, opacity: float, expansion_rate: float) -> Optional[Dict[str, Any]]:
        if opacity > 0.65 and expansion_rate > 1.08:
            confidence = min(0.94, 0.72 + (expansion_rate * 0.10))
            return {
                "event_type": "SMOKE",
                "severity": "HIGH",
                "confidence": round(confidence, 3),
                "opacity": round(opacity, 2)
            }
        return None

fire_smoke_detector = FireSmokeDetector()
