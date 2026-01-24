# file: src/test_yolov8n_video.py

from ultralytics import YOLO
import cv2
import time

# 1. Load pretrained YOLOv8n (COCO)
model = YOLO("yolov8n.pt")

# 2. Open your road video
video_path = "data/road_video.mp4"
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: cannot open video {video_path}")
    exit(1)

prev_time = time.time()
frames = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break  # end of video

    # 3. Run inference on this frame
    results = model(frame, verbose=False)[0]

    # 4. Draw detections
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        label = f"{model.names[cls_id]} {conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # 5. FPS calculation (on laptop, just for reference)
    frames += 1
    now = time.time()
    if now - prev_time >= 1.0:
        fps = frames / (now - prev_time)
        print(f"Approx FPS on laptop: {fps:.2f}")
        frames = 0
        prev_time = now

    cv2.imshow("YOLOv8n - Road Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()