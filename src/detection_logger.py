"""
Logs every detection to local CSV with GPS metadata.
Also queues detections for upload to the cloud backend.
"""

import csv
import os
import json
import time
from datetime import datetime, timezone


class DetectionLogger:

    def __init__(self, log_dir="logs", upload_queue_dir="logs/queue"):
        self.log_dir = log_dir
        self.upload_queue_dir = upload_queue_dir
        self.buffer = []
        self.upload_buffer = []
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(upload_queue_dir, exist_ok=True)

        self.log_file = os.path.join(
            log_dir,
            f"detections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        self._init_csv()

    def _init_csv(self):
        with open(self.log_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp_utc", "latitude", "longitude", "altitude",
                "accuracy_m", "speed_kmh", "bearing",
                "class_name", "confidence",
                "bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2",
                "severity_score", "frame_id", "device_id",
            ])

    def log(self, detection, gps_data, frame_id, device_id="pi5-001"):
        """
        detection: (x1, y1, x2, y2, conf, class_id)
        gps_data: dict from PhoneGPSReader.get_location() or None
        """
        x1, y1, x2, y2, conf, class_id = detection
        class_names = ["barricade", "pothole"]
        class_name = class_names[class_id] if class_id < len(class_names) else "unknown"

        # Severity scoring
        bbox_area = (x2 - x1) * (y2 - y1)
        frame_area = 640 * 480
        area_ratio = bbox_area / frame_area if frame_area > 0 else 0
        severity = self._calculate_severity(conf, area_ratio)

        timestamp = datetime.now(timezone.utc).isoformat()
        lat = gps_data["lat"] if gps_data else 0.0
        lon = gps_data["lon"] if gps_data else 0.0

        row = {
            "timestamp_utc": timestamp,
            "latitude": lat,
            "longitude": lon,
            "altitude": gps_data.get("altitude", 0.0) if gps_data else 0.0,
            "accuracy_m": gps_data.get("accuracy", 0.0) if gps_data else 0.0,
            "speed_kmh": round(gps_data.get("speed_kmh", 0.0), 1) if gps_data else 0.0,
            "bearing": gps_data.get("bearing", 0.0) if gps_data else 0.0,
            "class_name": class_name,
            "confidence": round(conf, 4),
            "bbox_x1": x1, "bbox_y1": y1, "bbox_x2": x2, "bbox_y2": y2,
            "severity_score": round(severity, 2),
            "frame_id": frame_id,
            "device_id": device_id,
        }

        # Write to CSV
        self.buffer.append(list(row.values()))
        if len(self.buffer) >= 20:
            self._flush_csv()

        # Queue for cloud upload
        self.upload_buffer.append(row)
        if len(self.upload_buffer) >= 50:
            self._save_upload_batch()

    def _calculate_severity(self, confidence, area_ratio):
        area_score = min(area_ratio / 0.10, 1.0)
        severity = (confidence * 0.4 + area_score * 0.6) * 10
        return max(1.0, min(10.0, severity))

    def _flush_csv(self):
        if not self.buffer:
            return
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.buffer)
        self.buffer.clear()

    def _save_upload_batch(self):
        """Save a batch of detections as JSON for later upload."""
        if not self.upload_buffer:
            return
        fname = f"batch_{int(time.time())}_{len(self.upload_buffer)}.json"
        path = os.path.join(self.upload_queue_dir, fname)
        with open(path, "w") as f:
            json.dump(self.upload_buffer, f)
        print(f"[Logger] Queued {len(self.upload_buffer)} detections for upload")
        self.upload_buffer.clear()

    def flush_all(self):
        self._flush_csv()
        self._save_upload_batch()