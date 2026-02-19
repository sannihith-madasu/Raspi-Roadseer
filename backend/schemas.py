from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# --- Incoming from Pi ---

class ReportIn(BaseModel):
    timestamp_utc: str
    latitude: float
    longitude: float
    altitude: Optional[float] = 0.0
    accuracy_m: Optional[float] = 0.0
    speed_kmh: Optional[float] = 0.0
    bearing: Optional[float] = 0.0
    class_name: str
    confidence: float
    bbox_x1: int
    bbox_y1: int
    bbox_x2: int
    bbox_y2: int
    severity_score: float
    frame_id: Optional[int] = 0
    device_id: Optional[str] = "unknown"


class BatchUpload(BaseModel):
    device_id: str
    detections: List[ReportIn]


# --- Outgoing to Frontend ---

class DetectionOut(BaseModel):
    id: int
    latitude: float
    longitude: float
    class_name: str
    avg_confidence: float
    max_confidence: float
    severity_score: float
    report_count: int
    first_reported: datetime
    last_reported: datetime
    status: str
    ward: Optional[str]
    road_name: Optional[str]
    avg_speed_kmh: float

    class Config:
        from_attributes = True


class StatsOut(BaseModel):
    total_detections: int
    critical_count: int
    moderate_count: int
    low_count: int
    pothole_count: int
    barricade_count: int
    total_reports: int
    active_devices: int
    avg_severity: float
    wards_affected: int


class WardReport(BaseModel):
    ward: str
    total_detections: int
    critical: int
    moderate: int
    low: int
    total_reports: int
    worst_severity: float
    top_potholes: List[DetectionOut]