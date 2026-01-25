# file: src/test_pothole_onnx_image.py

import cv2
import numpy as np
import onnxruntime as ort

ONNX_PATH = "models/pothole_yolov8n_best.onnx"
IMG_PATH = "datasets/potholes_kaggle/images/val/pothole_1284.jpg"  
IMG_SIZE = 512  # from export log: (1, 3, 512, 512)

session = ort.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

img = cv2.imread(IMG_PATH)
if img is None:
    raise FileNotFoundError(f"Could not read image: {IMG_PATH}")

h, w, _ = img.shape

img_resized = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
img_norm = img_rgb.astype(np.float32) / 255.0
img_input = np.transpose(img_norm, (2, 0, 1))  # HWC -> CHW
img_input = np.expand_dims(img_input, axis=0)

outputs = session.run([output_name], {input_name: img_input})[0]
print("ONNX output shape:", outputs.shape)