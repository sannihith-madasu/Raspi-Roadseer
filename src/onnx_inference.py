"""
Full RoadSeer inference pipeline:
  Camera → YOLO → GPS Tag → Log → Upload

This replaces your original onnx_inference.py
"""

import cv2
import numpy as np
import onnxruntime as ort
from picamera2 import Picamera2
import time
import argparse

from gps_reader import PhoneGPSReader
from detection_logger import DetectionLogger
from cloud_uploader import CloudUploader

# ============================================================
# CONFIG
# ============================================================
MODEL_PATH = "models/exported_models/yolo26n_fine_tuned_int8.onnx"
IMGSZ = 320
CONF_THRESHOLD = 0.5
CLASS_NAMES = ["barricade", "pothole"]
COLORS = [(0, 165, 255), (0, 0, 255)]

# ============================================================
# ARGS
# ============================================================
parser = argparse.ArgumentParser(description="RoadSeer Detection")
parser.add_argument("--phone-ip", type=str, default="192.168.1.42",
                    help="Phone GPS server IP address")
parser.add_argument("--phone-port", type=int, default=5000,
                    help="Phone GPS server port")
parser.add_argument("--device-id", type=str, default="pi5-001",
                    help="Unique ID for this device")
parser.add_argument("--api-url", type=str, default="http://localhost:8000",
                    help="Cloud backend URL")
parser.add_argument("--no-display", action="store_true",
                    help="Run headless (no cv2 window)")
args = parser.parse_args()

# ============================================================
# 1. INIT EVERYTHING
# ============================================================
print("=" * 50)
print("  ROADSEER — Full Pipeline")
print("=" * 50)

# Model
print("[1/4] Loading model...")
sess_options = ort.SessionOptions()
sess_options.intra_op_num_threads = 4
sess_options.inter_op_num_threads = 1
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

session = ort.InferenceSession(
    MODEL_PATH, sess_options=sess_options,
    providers=["CPUExecutionProvider"],
)
input_name = session.get_inputs()[0].name

# GPS
print(f"[2/4] Connecting to phone GPS at {args.phone_ip}:{args.phone_port}...")
gps = PhoneGPSReader(phone_ip=args.phone_ip, port=args.phone_port)
gps.start()

# Logger
print("[3/4] Starting detection logger...")
logger = DetectionLogger(log_dir="logs")

# Uploader
print(f"[4/4] Starting cloud uploader → {args.api_url}")
uploader = CloudUploader(
    api_url=args.api_url,
    queue_dir="logs/queue",
    device_id=args.device_id,
)
uploader.start()


# ============================================================
# 2. PREPROCESS / POSTPROCESS / DRAW (same as before)
# ============================================================
def preprocess(frame):
    orig_h, orig_w = frame.shape[:2]
    resized = cv2.resize(frame, (IMGSZ, IMGSZ), interpolation=cv2.INTER_LINEAR)
    img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img, orig_w / IMGSZ, orig_h / IMGSZ


def postprocess(output, scale_x, scale_y, conf_threshold=CONF_THRESHOLD):
    detections = []
    for det in output[0]:
        x1, y1, x2, y2, conf, class_id = det
        if conf < conf_threshold:
            continue
        detections.append((
            int(x1 * scale_x), int(y1 * scale_y),
            int(x2 * scale_x), int(y2 * scale_y),
            float(conf), int(class_id)
        ))
    return detections


def draw_detections(frame, detections, fps, gps_data):
    for (x1, y1, x2, y2, conf, class_id) in detections:
        color = COLORS[class_id] if class_id < len(COLORS) else (255, 255, 255)
        label = f"{CLASS_NAMES[class_id]} {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    # GPS status
    if gps_data:
        gps_text = f"GPS: {gps_data['lat']:.5f}, {gps_data['lon']:.5f} | {gps_data['speed_kmh']:.0f} km/h"
        cv2.putText(frame, gps_text, (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    else:
        cv2.putText(frame, "GPS: No fix", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    return frame


# ============================================================
# 3. CAMERA + MAIN LOOP
# ============================================================
print("\nStarting camera...")
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

# Warmup
print("Warming up model...")
dummy = np.random.randn(1, 3, IMGSZ, IMGSZ).astype(np.float32)
for _ in range(5):
    session.run(None, {input_name: dummy})

print("\n🚗 RoadSeer running! Press 'q' to quit.\n")

frame_count = 0
fps = 0.0
fps_start = time.time()
total_detections = 0

try:
    while True:
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        img_tensor, scale_x, scale_y = preprocess(frame_bgr)
        outputs = session.run(None, {input_name: img_tensor})
        detections = postprocess(outputs[0], scale_x, scale_y)

        # Get GPS
        gps_data = gps.get_location()

        # Log each detection
        for det in detections:
            logger.log(det, gps_data, frame_count, device_id=args.device_id)
            total_detections += 1

        # FPS
        frame_count += 1
        if frame_count % 10 == 0:
            fps = 10.0 / (time.time() - fps_start)
            fps_start = time.time()

        # Display
        if not args.no_display:
            display = draw_detections(frame_bgr, detections, fps, gps_data)
            cv2.imshow("RoadSeer", display)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Console status every 100 frames
        if frame_count % 100 == 0:
            fix_status = "✓" if gps_data else "✗"
            print(f"[Frame {frame_count}] FPS={fps:.1f} | "
                  f"GPS={fix_status} | "
                  f"Total detections={total_detections}")

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    logger.flush_all()
    gps.stop()
    uploader.stop()
    picam2.close()
    if not args.no_display:
        cv2.destroyAllWindows()
    print(f"\nDone. {total_detections} total detections logged.")