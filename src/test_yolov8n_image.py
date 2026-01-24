# file: src/test_yolov8n_image.py

from ultralytics import YOLO
import cv2

# 1. Load a pretrained YOLOv8n model.
#    This file (yolov8n.pt) will be downloaded automatically the first time.
model = YOLO("yolov8n.pt")

# 2. Read your test road image.
img_path = "data/road1.jpg"
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Could not read image at {img_path}")

# 3. Run the model on the image.
results = model(img)[0]  # results is a list; take first (and only) item

# 4. Loop over all detected objects and draw boxes.
for box in results.boxes:
    # box.xyxy[0] = [x1, y1, x2, y2] in image coordinates
    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
    conf = float(box.conf[0])  # confidence score
    cls_id = int(box.cls[0])   # class index: 0=person, 2=car, etc.
    label = f"{model.names[cls_id]} {conf:.2f}"  # e.g. "car 0.94"

    # Draw rectangle.
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # Draw label.
    cv2.putText(img, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

# 5. Show the result.
cv2.imshow("YOLOv8n - Road Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()