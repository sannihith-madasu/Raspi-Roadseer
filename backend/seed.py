"""
Seeds the database with 150 realistic detections around Hyderabad.
Run once:  cd backend && python seed.py

Delete roadseer.db first if you want a fresh start.
"""

import random
from datetime import datetime, timedelta, timezone
from database import engine, SessionLocal, Base
from models import Detection, Device

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Ward → realistic GPS center + roads in that area
WARDS = {
    "Jubilee Hills": {
        "center": (17.4325, 78.4072),
        "roads": ["Road No. 36", "Road No. 45", "Jubilee Hills Check Post Road"],
    },
    "Banjara Hills": {
        "center": (17.4156, 78.4347),
        "roads": ["Road No. 12", "Road No. 1", "Panjagutta Circle"],
    },
    "Madhapur": {
        "center": (17.4484, 78.3908),
        "roads": ["Hitech City Main Road", "Ayyappa Society Road", "Madhapur Junction Road"],
    },
    "Gachibowli": {
        "center": (17.4401, 78.3489),
        "roads": ["Biodiversity Junction", "Gachibowli Flyover Road", "ISB Road"],
    },
    "Kukatpally": {
        "center": (17.4947, 78.3996),
        "roads": ["JNTU-Kukatpally Road", "KPHB Colony Road", "Kukatpally Y Junction Road"],
    },
    "Ameerpet": {
        "center": (17.4374, 78.4482),
        "roads": ["Ameerpet Metro Road", "SR Nagar Cross Road", "Greenlands Road"],
    },
    "Secunderabad": {
        "center": (17.4399, 78.4983),
        "roads": ["Tank Bund Road", "MG Road", "Paradise Circle Road"],
    },
    "Begumpet": {
        "center": (17.4440, 78.4675),
        "roads": ["Begumpet Airport Road", "Sardar Patel Road", "Rasoolpura Main Road"],
    },
    "Kondapur": {
        "center": (17.4589, 78.3726),
        "roads": ["Kondapur Main Road", "Botanical Garden Road", "Jayabheri Road"],
    },
    "Miyapur": {
        "center": (17.4969, 78.3548),
        "roads": ["Miyapur X Roads", "Allwyn Colony Road", "Miyapur Metro Station Road"],
    },
    "Dilsukhnagar": {
        "center": (17.3687, 78.5247),
        "roads": ["Dilsukhnagar Bus Stop Road", "Moosarambagh Road", "Chaitanyapuri Main Road"],
    },
    "LB Nagar": {
        "center": (17.3457, 78.5522),
        "roads": ["LB Nagar Circle Road", "Sagar Ring Road", "Vanasthalipuram Main Road"],
    },
}


def random_near(center_lat, center_lon, radius_km=1.0):
    """Random GPS point within radius_km of center."""
    offset = radius_km * 0.009
    lat = center_lat + (random.random() - 0.5) * 2 * offset
    lon = center_lon + (random.random() - 0.5) * 2 * offset
    return round(lat, 6), round(lon, 6)


def seed():
    db = SessionLocal()

    # Check if already seeded
    existing = db.query(Detection).count()
    if existing > 0:
        print(f"Database already has {existing} detections. Delete roadseer.db to re-seed.")
        db.close()
        return

    print("Seeding database with 150 detections...")

    # Create 5 devices
    devices = []
    for i in range(1, 6):
        dev = Device(
            device_id=f"PI5-{str(i).zfill(3)}",
            label=f"Auto #{i}",
            last_seen=datetime.now(timezone.utc),
            total_reports=0,
            is_active=True,
        )
        db.add(dev)
        devices.append(dev)

    # Store raw values separately so we don't touch ORM objects after close
    severity_scores = []
    class_names = []
    report_counts = []

    ward_names = list(WARDS.keys())

    for i in range(150):
        ward_name = random.choice(ward_names)
        ward = WARDS[ward_name]
        lat, lon = random_near(ward["center"][0], ward["center"][1], radius_km=1.5)
        road = random.choice(ward["roads"])

        severity = round(random.uniform(2.5, 9.5), 1)
        confidence = round(random.uniform(0.55, 0.90), 2)
        class_name = "pothole" if random.random() > 0.2 else "barricade"
        report_count = random.randint(1, 40)
        speed = round(random.uniform(10, 50), 1)

        days_ago = random.randint(0, 30)
        first = datetime.now(timezone.utc) - timedelta(days=days_ago)
        last = datetime.now(timezone.utc) - timedelta(days=random.randint(0, days_ago))

        det = Detection(
            latitude=lat,
            longitude=lon,
            class_name=class_name,
            avg_confidence=confidence,
            max_confidence=round(min(confidence + random.uniform(0, 0.1), 0.99), 2),
            severity_score=severity,
            report_count=report_count,
            first_reported=first,
            last_reported=last,
            status="active",
            ward=ward_name,
            road_name=road,
            avg_speed_kmh=speed,
        )
        db.add(det)

        # Save raw values
        severity_scores.append(severity)
        class_names.append(class_name)
        report_counts.append(report_count)

    # Update device total_reports
    total_reports = sum(report_counts)
    for dev in devices:
        dev.total_reports = total_reports // 5

    db.commit()
    db.close()

    # Print summary using saved plain values (not ORM objects)
    critical = sum(1 for s in severity_scores if s >= 7)
    moderate = sum(1 for s in severity_scores if 4 <= s < 7)
    low = sum(1 for s in severity_scores if s < 4)
    potholes = sum(1 for c in class_names if c == "pothole")

    print(f"\n✅ Seeded 150 detections + 5 devices")
    print(f"   Potholes: {potholes} | Barricades: {150 - potholes}")
    print(f"   Critical: {critical} | Moderate: {moderate} | Low: {low}")
    print(f"   Wards: {len(WARDS)}")
    print(f"\n   Test: http://localhost:8000/api/detections")
    print(f"   Test: http://localhost:8000/api/stats")


if __name__ == "__main__":
    seed()