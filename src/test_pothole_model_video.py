# file: src/test_pothole_model_video.py

from ultralytics import YOLO
import cv2
import time

MODEL_PATH = "models/pothole_yolov8n_best.pt"  # adjust if needed
VIDEO_PATH = "datasets/potholes_kaggle/sample_video.mp4"  # or your own video

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

    results = model(frame, verbose=False)[0]

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
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