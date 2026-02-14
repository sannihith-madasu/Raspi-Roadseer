import cv2
import numpy as np
import onnxruntime as ort
from picamera2 import Picamera2
import time

# ============================================================
# CONFIGURATION
# ============================================================
MODEL_PATH = "models/exported_models/yolo26n_fine_tuned_int8.onnx"
IMGSZ = 320
CONF_THRESHOLD = 0.5
CLASS_NAMES = ["pothole", "barricade"]
COLORS = [(0, 0, 255), (0, 165, 255)]  # Red for pothole, Orange for barricade

# ============================================================
# 1. LOAD MODEL
# ============================================================
print("Loading model...")
sess_options = ort.SessionOptions()
sess_options.intra_op_num_threads = 4        # Use all 4 Pi 5 cores
sess_options.inter_op_num_threads = 1
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

session = ort.InferenceSession(
    MODEL_PATH,
    sess_options=sess_options,
    providers=["CPUExecutionProvider"],
)
input_name = session.get_inputs()[0].name
print(f"Model loaded. Input: {input_name}, shape: {session.get_inputs()[0].shape}")


# ============================================================
# 2. PREPROCESSING
# ============================================================
def preprocess(frame):
    """
    Resize, normalize, convert to NCHW float32 tensor.
    Returns preprocessed tensor and scale factors for box mapping.
    """
    orig_h, orig_w = frame.shape[:2]

    # Resize to model input size
    resized = cv2.resize(frame, (IMGSZ, IMGSZ), interpolation=cv2.INTER_LINEAR)

    # BGR → RGB, normalize to [0, 1], HWC → CHW, add batch dim
    img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)

    # Scale factors to map boxes back to original frame size
    scale_x = orig_w / IMGSZ
    scale_y = orig_h / IMGSZ

    return img, scale_x, scale_y


# ============================================================
# 3. POSTPROCESSING
# ============================================================
def postprocess(output, scale_x, scale_y, conf_threshold=CONF_THRESHOLD):
    """
    Parse YOLO26 output: [1, 300, 6] → [x1, y1, x2, y2, confidence, class_id]
    Returns list of (x1, y1, x2, y2, confidence, class_id) in original frame coords.
    """
    detections = []
    output = output[0]  # Remove batch dim → [300, 6]

    for det in output:
        x1, y1, x2, y2, conf, class_id = det
        if conf < conf_threshold:
            continue

        # Scale boxes back to original frame size
        x1 = int(x1 * scale_x)
        y1 = int(y1 * scale_y)
        x2 = int(x2 * scale_x)
        y2 = int(y2 * scale_y)
        class_id = int(class_id)

        detections.append((x1, y1, x2, y2, float(conf), class_id))

    return detections


# ============================================================
# 4. DRAW DETECTIONS
# ============================================================
def draw_detections(frame, detections, fps):
    for (x1, y1, x2, y2, conf, class_id) in detections:
        color = COLORS[class_id] if class_id < len(COLORS) else (255, 255, 255)
        label = f"{CLASS_NAMES[class_id]} {conf:.2f}"

        # Draw box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Draw label background
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame, (x1, y1 - text_h - 10), (x1 + text_w, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # FPS counter
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    return frame


# ============================================================
# 5. MAIN LOOP — Camera → Detect → Display
# ============================================================
print("Starting camera...")
picam2 = Picamera2()

# Configure camera — use a resolution the Pi can handle smoothly
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

print("Running detection... Press 'q' to quit.\n")

frame_count = 0
fps = 0.0
fps_start = time.time()

try:
    while True:
        # Capture frame
        frame = picam2.capture_array()

        # Convert RGB → BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Preprocess
        img_tensor, scale_x, scale_y = preprocess(frame_bgr)

        # Inference
        outputs = session.run(None, {input_name: img_tensor})

        # Postprocess
        detections = postprocess(outputs[0], scale_x, scale_y)

        # Calculate FPS
        frame_count += 1
        if frame_count % 10 == 0:
            fps = 10.0 / (time.time() - fps_start)
            fps_start = time.time()

        # Draw and display
        display = draw_detections(frame_bgr, detections, fps)
        cv2.imshow("RoadSeer - Pothole & Barricade Detection", display)

        # Print detections to console
        if detections:
            for (x1, y1, x2, y2, conf, cls) in detections:
                print(f"  [{CLASS_NAMES[cls]}] conf={conf:.2f} box=({x1},{y1})-({x2},{y2})")

        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    picam2.close()
    cv2.destroyAllWindows()
    print("Done.")