# file: src/test_pothole_tflite_video_boxes.py

import cv2
import numpy as np
import time
import tflite_runtime.interpreter as tflite

TFLITE_PATH = "models/pothole_yolov8n_best_float16.tflite"  # or _float32.tflite
IMG_SIZE = 512
CONF_THRESH = 0.4
IOU_THRESH = 0.45

CLASS_NAMES = ["pothole"]

interpreter = tflite.Interpreter(model_path=TFLITE_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_index = input_details[0]["index"]
output_index = output_details[0]["index"]

input_scale, input_zero_point = input_details[0].get("quantization", (1.0, 0))
output_scale, output_zero_point = output_details[0].get("quantization", (1.0, 0))

def xywh_to_xyxy(xywh):
    x, y, w, h = xywh.T
    x1 = x - w / 2
    y1 = y - h / 2
    x2 = x + w / 2
    y2 = y + h / 2
    return np.stack([x1, y1, x2, y2], axis=1)

def nms(boxes, scores, iou_threshold):
    if len(boxes) == 0:
        return []
    boxes = boxes.astype(np.float32)
    x1, y1, x2, y2 = boxes.T
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y1[i], y1[order[1:]])
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)
        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]
    return keep

VIDEO_PATH = "data/road_video.mp4"
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Cannot open video: {VIDEO_PATH}")

prev_time = time.time()
frames = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    orig_h, orig_w, _ = frame.shape

    img_resized = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    img_norm = img_rgb.astype(np.float32) / 255.0

    # For float16/float32 models, inputs are float
    input_data = np.expand_dims(img_norm, axis=0).astype(input_details[0]["dtype"])

    interpreter.set_tensor(input_index, input_data)
    interpreter.invoke()
    outputs = interpreter.get_tensor(output_index)[0]  # expected (5, N)

    # Dequantize if needed (for int8/uint8 outputs, not for float)
    if output_details[0]["dtype"] != np.float32:
        outputs = (outputs.astype(np.float32) - output_zero_point) * output_scale

    xywh = outputs[:4, :].T
    scores = outputs[4, :]

    mask = scores > CONF_THRESH
    xywh = xywh[mask]
    scores_f = scores[mask]

    boxes_xyxy = xywh_to_xyxy(xywh)

    scale_x = orig_w / IMG_SIZE
    scale_y = orig_h / IMG_SIZE
    boxes_xyxy[:, 0] *= scale_x
    boxes_xyxy[:, 2] *= scale_x
    boxes_xyxy[:, 1] *= scale_y
    boxes_xyxy[:, 3] *= scale_y

    keep = nms(boxes_xyxy, scores_f, IOU_THRESH)
    boxes_xyxy = boxes_xyxy[keep]
    scores_f = scores_f[keep]

    for box, score in zip(boxes_xyxy, scores_f):
        x1, y1, x2, y2 = box.astype(int)
        label = f"{CLASS_NAMES[0]} {score:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame, label, (x1, max(0, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA
        )

    frames += 1
    now = time.time()
    if now - prev_time >= 1.0:
        fps = frames / (now - prev_time)
        print(f"FPS (TFLite, {IMG_SIZE}x{IMG_SIZE}): {fps:.2f}")
        frames = 0
        prev_time = now

    cv2.imshow("Pothole detection (TFLite)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()