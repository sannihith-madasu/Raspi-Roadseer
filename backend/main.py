"""
RoadSeer Cloud Backend

Endpoints:
  POST /api/detections/batch   ← Pi uploads batches here
  GET  /api/detections         ← Frontend fetches all detections
  GET  /api/stats              ← Frontend fetches aggregate stats
  GET  /api/reports            ← Frontend fetches ward-wise reports
  GET  /api/devices            ← Frontend fetches active devices
"""

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import Optional

from database import engine, get_db, Base
from models import Detection, RawReport, Device
from schemas import BatchUpload, DetectionOut, StatsOut, WardReport
from deduplication import find_or_create_detection

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RoadSeer API", version="1.0.0")

# CORS — allow your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# UPLOAD ENDPOINT (Pi → Cloud)
# ─────────────────────────────────────────────
@app.post("/api/detections/batch")
def upload_batch(batch: BatchUpload, db: Session = Depends(get_db)):
    """Receive a batch of detections from a Pi device."""
    new_count = 0
    merged_count = 0

    # Upsert device
    device = db.query(Device).filter(Device.device_id == batch.device_id).first()
    if not device:
        device = Device(device_id=batch.device_id)
        db.add(device)
    device.last_seen = datetime.now(timezone.utc)
    device.total_reports = (device.total_reports or 0) + len(batch.detections)

    for report in batch.detections:
        # Skip if no GPS fix
        if report.latitude == 0.0 and report.longitude == 0.0:
            continue

        # Save raw report
        raw = RawReport(
            device_id=batch.device_id,
            latitude=report.latitude,
            longitude=report.longitude,
            altitude=report.altitude,
            accuracy_m=report.accuracy_m,
            speed_kmh=report.speed_kmh,
            bearing=report.bearing,
            class_name=report.class_name,
            confidence=report.confidence,
            severity_score=report.severity_score,
            bbox_x1=report.bbox_x1,
            bbox_y1=report.bbox_y1,
            bbox_x2=report.bbox_x2,
            bbox_y2=report.bbox_y2,
            timestamp_utc=datetime.fromisoformat(report.timestamp_utc),
        )
        db.add(raw)
        db.flush()  # get raw.id

        # Deduplicate
        detection, is_new = find_or_create_detection(
            db, report.latitude, report.longitude,
            report.class_name, report.confidence,
            report.severity_score, report.speed_kmh or 0.0,
        )
        db.flush()
        raw.detection_id = detection.id

        if is_new:
            new_count += 1
        else:
            merged_count += 1

    db.commit()

    return {
        "status": "ok",
        "new_detections": new_count,
        "merged_reports": merged_count,
        "total_processed": len(batch.detections),
    }


# ─────────────────────────────────────────────
# FRONTEND ENDPOINTS
# ─────────────────────────────────────────────
@app.get("/api/detections", response_model=list[DetectionOut])
def get_detections(
    status: Optional[str] = Query("active"),
    class_name: Optional[str] = None,
    min_severity: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Get all detections (for the map and list views)."""
    q = db.query(Detection)
    if status:
        q = q.filter(Detection.status == status)
    if class_name:
        q = q.filter(Detection.class_name == class_name)
    if min_severity:
        q = q.filter(Detection.severity_score >= min_severity)
    return q.order_by(Detection.severity_score.desc()).all()


@app.get("/api/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    """Aggregate stats for the dashboard."""
    detections = db.query(Detection).filter(Detection.status == "active").all()
    total_reports = db.query(func.sum(Detection.report_count)).scalar() or 0
    active_devices = db.query(Device).filter(Device.is_active == True).count()

    critical = sum(1 for d in detections if d.severity_score >= 7)
    moderate = sum(1 for d in detections if 4 <= d.severity_score < 7)
    low = sum(1 for d in detections if d.severity_score < 4)
    potholes = sum(1 for d in detections if d.class_name == "pothole")

    avg_sev = (
        sum(d.severity_score for d in detections) / len(detections)
        if detections else 0.0
    )

    wards = set(d.ward for d in detections if d.ward)

    return StatsOut(
        total_detections=len(detections),
        critical_count=critical,
        moderate_count=moderate,
        low_count=low,
        pothole_count=potholes,
        barricade_count=len(detections) - potholes,
        total_reports=total_reports,
        active_devices=active_devices,
        avg_severity=round(avg_sev, 1),
        wards_affected=len(wards),
    )


@app.get("/api/reports", response_model=list[WardReport])
def get_ward_reports(db: Session = Depends(get_db)):
    """Ward-wise reports for the municipal reports page."""
    detections = db.query(Detection).filter(Detection.status == "active").all()

    wards = {}
    for d in detections:
        ward = d.ward or "Unknown"
        if ward not in wards:
            wards[ward] = []
        wards[ward].append(d)

    reports = []
    for ward, dets in wards.items():
        critical = sum(1 for d in dets if d.severity_score >= 7)
        moderate = sum(1 for d in dets if 4 <= d.severity_score < 7)
        low = sum(1 for d in dets if d.severity_score < 4)
        total_reports = sum(d.report_count for d in dets)
        worst = max(d.severity_score for d in dets)
        top = sorted(dets, key=lambda x: x.severity_score, reverse=True)[:5]

        reports.append(WardReport(
            ward=ward,
            total_detections=len(dets),
            critical=critical,
            moderate=moderate,
            low=low,
            total_reports=total_reports,
            worst_severity=worst,
            top_potholes=top,
        ))

    return sorted(reports, key=lambda r: r.worst_severity, reverse=True)


@app.get("/api/devices")
def get_devices(db: Session = Depends(get_db)):
    """List all registered devices."""
    return db.query(Device).order_by(Device.last_seen.desc()).all()


@app.patch("/api/detections/{detection_id}/resolve")
def resolve_detection(detection_id: int, db: Session = Depends(get_db)):
    """Mark a pothole as resolved (municipality fixed it)."""
    det = db.query(Detection).filter(Detection.id == detection_id).first()
    if det:
        det.status = "resolved"
        db.commit()
        return {"status": "resolved", "id": detection_id}
    return {"error": "not found"}, 404