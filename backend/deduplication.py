"""
Deduplication logic:
If a new report is within DEDUP_RADIUS_M meters of an existing Detection
with the same class_name, merge it instead of creating a new one.
"""

from math import radians, sin, cos, sqrt, atan2
from sqlalchemy.orm import Session
from models import Detection


DEDUP_RADIUS_M = 20  # meters


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def find_or_create_detection(db: Session, lat, lon, class_name, confidence, severity, speed):
    """
    Find an existing Detection within DEDUP_RADIUS_M, or create a new one.
    Returns (detection, is_new)
    """
    # Rough bounding box filter first (for DB performance)
    # ~0.0002 degrees ≈ 20 meters
    offset = 0.0003
    candidates = db.query(Detection).filter(
        Detection.class_name == class_name,
        Detection.status == "active",
        Detection.latitude.between(lat - offset, lat + offset),
        Detection.longitude.between(lon - offset, lon + offset),
    ).all()

    # Fine check with haversine
    for det in candidates:
        dist = haversine(lat, lon, det.latitude, det.longitude)
        if dist <= DEDUP_RADIUS_M:
            # Merge: update running averages
            n = det.report_count
            det.latitude = (det.latitude * n + lat) / (n + 1)      # weighted average location
            det.longitude = (det.longitude * n + lon) / (n + 1)
            det.avg_confidence = (det.avg_confidence * n + confidence) / (n + 1)
            det.max_confidence = max(det.max_confidence, confidence)
            det.severity_score = max(det.severity_score, severity)
            det.avg_speed_kmh = (det.avg_speed_kmh * n + speed) / (n + 1)
            det.report_count += 1
            return det, False

    # New detection
    new_det = Detection(
        latitude=lat,
        longitude=lon,
        class_name=class_name,
        avg_confidence=confidence,
        max_confidence=confidence,
        severity_score=severity,
        report_count=1,
        avg_speed_kmh=speed,
    )
    db.add(new_det)
    return new_det, True