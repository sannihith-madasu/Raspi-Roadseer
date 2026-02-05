# file: src/test_pothole_model_video.py

from ultralytics import YOLO
import cv2
import time

MODEL_PATH = "models/pothole_barricade_custom_model.pt"  # adjust if needed
VIDEO_PATH = "data/testcase5.mp4"  # or your own video

# ROI Configuration: Ignore bottom % of frame (where car bonnet appears)
IGNORE_BOTTOM_PERCENT = 0.0  # Adjust this value (0.2 = bottom 20%, 0.3 = bottom 30%)
MIN_CONFIDENCE = 0.5  # Minimum confidence threshold to reduce false positives

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Cannot open video: {VIDEO_PATH}")

prev_time = time.time()
frames = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_height, frame_width = frame.shape[:2]
    roi_threshold = int(frame_height * (1 - IGNORE_BOTTOM_PERCENT))
    
    results = model(frame, verbose=False)[0]

    # Draw ROI line (optional visualization)
    cv2.line(frame, (0, roi_threshold), (frame_width, roi_threshold), (255, 0, 0), 2)
    cv2.putText(frame, "Detection Zone Above", (10, roi_threshold - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        
        # Filter 1: Check if bounding box center is above ROI threshold
        box_center_y = (y1 + y2) / 2
        if box_center_y > roi_threshold:
            continue  # Skip detections in bonnet area
        
        # Filter 2: Check confidence threshold
        if conf < MIN_CONFIDENCE:
            continue  # Skip low-confidence detections
        
        label = f"{model.names[cls_id]} {conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    frames += 1
    now = time.time()
    if now - prev_time >= 1.0:
        fps = frames / (now - prev_time)
        print(f"FPS: {fps:.2f}")
        frames = 0
        prev_time = now

    cv2.imshow("Pothole Model - Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()