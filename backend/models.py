from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base


class Detection(Base):
    """
    A single deduplicated pothole/barricade location.
    Multiple raw reports get merged into one Detection.
    """
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    class_name = Column(String, nullable=False, index=True)       # "pothole" or "barricade"
    avg_confidence = Column(Float, default=0.0)
    max_confidence = Column(Float, default=0.0)
    severity_score = Column(Float, default=0.0)
    report_count = Column(Integer, default=1)
    first_reported = Column(DateTime(timezone=True), server_default=func.now())
    last_reported = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(String, default="active")                      # active, resolved, disputed
    ward = Column(String, nullable=True)
    road_name = Column(String, nullable=True)
    avg_speed_kmh = Column(Float, default=0.0)


class RawReport(Base):
    """
    Every single report from every device.
    Linked to a Detection after deduplication.
    """
    __tablename__ = "raw_reports"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, nullable=True, index=True)      # linked after dedup
    device_id = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, default=0.0)
    accuracy_m = Column(Float, default=0.0)
    speed_kmh = Column(Float, default=0.0)
    bearing = Column(Float, default=0.0)
    class_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    severity_score = Column(Float, default=0.0)
    bbox_x1 = Column(Integer)
    bbox_y1 = Column(Integer)
    bbox_x2 = Column(Integer)
    bbox_y2 = Column(Integer)
    timestamp_utc = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Device(Base):
    """Registered Pi devices."""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    device_id = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=True)          # "Auto #42", "Bus Route 5"
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    total_reports = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)