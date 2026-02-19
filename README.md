# 🛣️ Raspi-RoadSeer

**Real-Time Road Anomaly Detection from Dashcam Footage on Raspberry Pi 5**

> Bharat AI-SoC Student Challenge 2026 — Edge AI for Smart Cities

Raspi-RoadSeer is a crowdsourced road quality monitoring system that detects potholes and barricades in real-time using a camera mounted on a Raspberry Pi 5. Detections are GPS-tagged, severity-scored, deduplicated across devices, and visualized on an interactive web dashboard with ward-wise municipal reports.

---

## 📐 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        LAPTOP / SERVER                           │
│                                                                  │
│  ┌───────────────┐    localhost:8000     ┌───────────────────┐   │
│  │   Frontend    │ ──────────────────►   │     Backend       │   │
│  │  React+Vite   │                       │   FastAPI+SQLite  │   │
│  │  port 5173    │ ◄──────────────────   │   port 8000       │   │
│  └───────────────┘    JSON responses     └───────────────────┘   │
│         ▲                                        ▲               │
│         │ Browser                                │               │
└─────────┼────────────────────────────────────────┼───────────────┘
                                                   │ WiFi
                                         ┌─────────┴───────────┐
                                         │   RASPBERRY PI 5    │
                                         │                     │
                                         │  Camera → YOLO      │
                                         │  Phone GPS →        │
                                         │  Logger → Uploader  │
                                         │  → POST to backend  │
                                         └─────────────────────┘
                                                   ▲
                                                   │ WiFi
                                         ┌─────────┴───────────┐
                                         │  SMARTPHONE         │
                                         │  GPS Server         │
                                         │  (Flask, port 5000) │
                                         └─────────────────────┘
```

## 🧠 Detection Pipeline

```
📷 Dashcam → 🧠 YOLO26n (INT8 ONNX) → 📍 GPS Tag → 📝 Severity Score → 📤 Cloud Upload → 🗺️ Dashboard
```

| Stage | What Happens |
|-------|-------------|
| **Capture** | Pi Camera Module captures frames at 640×480 |
| **Inference** | YOLO26n INT8 quantized ONNX model runs on CPU at ~15 FPS |
| **GPS Tagging** | Phone GPS coordinates attached to each detection via WiFi |
| **Severity Scoring** | Score 1–10 based on confidence (40%) + bounding box area ratio (60%) |
| **Local Logging** | Every detection saved to CSV (offline-first, never lose data) |
| **Cloud Upload** | Batches of 50 detections uploaded to backend every 30 seconds |
| **Deduplication** | Backend merges reports within 20m of each other using Haversine distance |
| **Dashboard** | React frontend shows interactive map, charts, ward-wise municipal reports |

---

## 📁 Project Structure

```
Raspi-Roadseer/
├── src/                        # Pi-side code (runs on Raspberry Pi)
│   ├── onnx_inference.py       # Main pipeline: Camera → YOLO → GPS → Log → Upload
│   ├── gps_reader.py           # Reads GPS from phone over WiFi
│   ├── detection_logger.py     # Logs to CSV + queues JSON batches for upload
│   ├── cloud_uploader.py       # Background thread: POSTs batches to backend
|   └── phone_gps_server.py     # Takes GPS values from phone and sends it to Raspberry Pi (runs on Termux)
│
├── models/                     # ONNX model files
│   └── exported_models/
│       └── yolo26n_fine_tuned_int8.onnx
│
├── backend/                    # Cloud backend (runs on laptop/server)
│   ├── main.py                 # FastAPI app with 6 REST endpoints
│   ├── models.py               # SQLAlchemy ORM models (Detection, RawReport, Device)
│   ├── schemas.py              # Pydantic validation schemas
│   ├── database.py             # SQLite connection setup
│   ├── deduplication.py        # Haversine-based spatial deduplication
│   ├── seed.py                 # Seed database with demo data
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # DATABASE_URL config
│
├── frontend/                   # Web dashboard (runs on laptop/server)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx     # Hero page with project overview
│   │   │   ├── MapView.jsx     # Interactive Leaflet map with filters
│   │   │   ├── Dashboard.jsx   # Analytics with charts (Recharts)
│   │   │   └── Reports.jsx     # Ward-wise municipal reports + CSV export
│   │   ├── data/
│   │   │   └── api.js          # API client (fetches from backend)
│   │   └── hooks/
│   │       └── useApi.js       # React hook for async data fetching
│   ├── package.json            # npm dependencies (install with npm install)
│   └── .env                    # VITE_API_URL config
│
└── requirements.txt            # Pi-side Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites

- **Raspberry Pi 5** with Pi Camera Module
- **Smartphone** on the same WiFi (for GPS)
- **Laptop** (runs backend + frontend)
- **Python 3.10+** on all devices
- **Node.js 18+** on laptop (for frontend)

### 1. Clone the Repository

```bash
git clone https://github.com/sannihith-madasu/Raspi-Roadseer.git
cd Raspi-Roadseer
```

### 2. Backend Setup (Laptop)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Start backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify: Open `http://localhost:8000/docs` for interactive API docs.

### 3. Frontend Setup (Laptop — new terminal)

```bash
cd frontend

# Install all dependencies (reads package.json automatically)
npm install

# Start development server
npm run dev
```

Open `http://localhost:5174` in your browser.

### 4. Pi Setup (Raspberry Pi)

```bash
# Clone repo on Pi
git clone https://github.com/sannihith-madasu/Raspi-Roadseer.git
cd Raspi-Roadseer

# Install Pi dependencies
pip install -r requirements.txt
pip install requests flask

# Run the full pipeline
python src/onnx_inference.py \
  --phone-ip <PHONE_IP> \
  --api-url http://<LAPTOP_IP>:8000 \
  --device-id pi5-001
```

> Replace `<PHONE_IP>` and `<LAPTOP_IP>` with actual IPs on your WiFi network.
> Find laptop IP: run `ipconfig` (Windows) or `ifconfig` (Linux/Mac).

### 5. Phone GPS Server (Android + Termux)

The Pi doesn't have a GPS module — your smartphone acts as a wireless GPS server instead. Install **[Termux](https://f-droid.org/en/packages/com.termux/)** and **[Termux:API](https://f-droid.org/en/packages/com.termux.api/)** from F-Droid (not Play Store), grant **Location permission** to Termux:API, then run `pkg install python termux-api && pip install flask` inside Termux. Start the server with `python phone_gps_server.py` — it polls `termux-location -p network` every 3 seconds in a background thread and serves coordinates via Flask on port 5000. The Pi fetches `http://<PHONE_IP>:5000/gps` each inference cycle and attaches lat/lon to every detection. Use `http://<PHONE_IP>:5000/health` to verify the GPS fix is active.

> **Note:** The server uses the `network` provider (WiFi/cell tower) instead of `gps` for faster, more reliable fixes indoors. Polling is set to 3s — faster intervals cause Termux:API `ResultReturner` errors. Keep the phone plugged in during demos and run `termux-wake-lock` to prevent Android from killing Termux in the background.
---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/detections/batch` | Upload batch of detections from Pi |
| `GET` | `/api/detections` | Get all detections (supports `?status=`, `?class_name=`, `?min_severity=` filters) |
| `GET` | `/api/stats` | Aggregate stats (total, critical, moderate, low, by class, devices, wards) |
| `GET` | `/api/reports` | Ward-wise breakdown with top 5 worst per ward |
| `GET` | `/api/devices` | List all registered Pi devices |
| `PATCH` | `/api/detections/{id}/resolve` | Mark a detection as resolved |

Full interactive docs available at `http://localhost:8000/docs` when backend is running.

---

## 🗺️ Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| **Landing** | `/` | Hero page with live stats, feature cards, pipeline diagram |
| **Map View** | `/map` | Interactive dark-themed Leaflet map with severity-colored markers, sidebar filters, search |
| **Dashboard** | `/dashboard` | Analytics with stat cards, ward breakdown bar chart, severity pie chart, 14-day trend |
| **Reports** | `/reports` | Ward-wise priority reports sorted by worst severity, CSV export per ward |

---

## 🧪 Deduplication

Multiple devices detecting the same pothole are merged using **Haversine distance**:

1. New detection arrives with lat/lon + class_name
2. SQL bounding box query finds candidates within ±30m
3. Haversine formula calculates exact distance
4. If **≤ 20 meters** and same class → **merge** (update confidence, severity, report count)
5. If no match → **create new** detection

This means 100 auto-rickshaws driving over the same pothole = 1 map marker with `report_count: 100`.

---

## 📊 Severity Scoring

```
severity = (confidence × 0.4 + area_ratio × 0.6) × 10
```

| Score | Level | Color |
|-------|-------|-------|
| 7.0 – 10.0 | 🔴 Critical | Red |
| 4.0 – 6.9 | 🟡 Moderate | Amber |
| 1.0 – 3.9 | 🟢 Low | Green |

- **confidence**: YOLO detection confidence (0–1)
- **area_ratio**: bounding box area ÷ frame area (larger pothole = higher severity)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Edge Inference** | YOLO26n, ONNX Runtime, INT8 Quantization |
| **Hardware** | Raspberry Pi 5 (Arm Cortex-A76), Pi Camera Module |
| **GPS** | Smartphone → Flask server → WiFi |
| **Backend** | Python, FastAPI, SQLAlchemy, SQLite |
| **Frontend** | React 19, Vite, Tailwind CSS 4, Leaflet, Recharts, Framer Motion |
| **Deduplication** | Haversine formula, spatial SQL queries |

---

## 👥 Team

Built for the **Bharat AI-SoC Student Challenge 2026** by [Sannihith Madasu](https://github.com/sannihith-madasu) and [Jeevan R](https://github.com/JeevanR15)

---

## 📄 License

This project is for hackathon demonstration purposes.
