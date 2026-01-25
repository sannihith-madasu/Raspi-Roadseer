# file: src/test_pothole_model_image.py

from ultralytics import YOLO
import cv2

# 1. Load your fine-tuned model
model_path = "runs/detect/train/weights/best.pt"  # adjust if path differs
model = YOLO(model_path)

# 2. Test image (pick any pothole image; you can use one from the dataset)
img_path = "data/kalagee.png"
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Could not read image: {img_path}")

# 3. Run inference
results = model(img)[0]

for box in results.boxes:
    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
    conf = float(box.conf[0])
    cls_id = int(box.cls[0])
    label = f"{model.names[cls_id]} {conf:.2f}"

    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

cv2.imshow("Pothole model - test image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()