"""
Runs on your Android phone inside Termux.
Serves GPS coordinates over HTTP so the Raspberry Pi can fetch them.

Setup:
  1. Install Termux from F-Droid
  2. pkg install python termux-api
  3. pip install flask
  4. Install "Termux:API" app from F-Droid
  5. Grant location permission to Termux:API
  6. python phone_gps_server.py

The Pi fetches: http://<phone-ip>:5000/gps
"""

from flask import Flask, jsonify
import subprocess
import json
import time
import threading

app = Flask(__name__)

gps_data = {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "speed": 0.0,
    "accuracy": 0.0,
    "bearing": 0.0,
    "timestamp": 0,
    "provider": "none",
    "fix": False,
}


def update_gps_loop():
    """Background thread: polls Termux location API every 3 seconds."""
    global gps_data
    while True:
        try:
            result = subprocess.run(
                ["termux-location", "-p", "network"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0 and result.stdout.strip():
                loc = json.loads(result.stdout)
                gps_data = {
                    "latitude": loc.get("latitude", 0.0),
                    "longitude": loc.get("longitude", 0.0),
                    "altitude": loc.get("altitude", 0.0),
                    "speed": loc.get("speed", 0.0),
                    "accuracy": loc.get("accuracy", 0.0),
                    "bearing": loc.get("bearing", 0.0),
                    "timestamp": time.time(),
                    "provider": loc.get("provider", "network"),
                    "fix": True,
                }
                print(f"GPS updated: {gps_data['latitude']:.6f}, {gps_data['longitude']:.6f} | accuracy: {gps_data['accuracy']:.1f}m")
        except subprocess.TimeoutExpired:
            print("GPS timeout — retrying...")
        except (json.JSONDecodeError, Exception) as e:
            print(f"GPS error: {e}")
        time.sleep(3)


@app.route("/gps")
def get_gps():
    """Pi fetches this endpoint."""
    if time.time() - gps_data["timestamp"] > 10:
        gps_data["fix"] = False
    return jsonify(gps_data)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "gps_fix": gps_data["fix"]})


if __name__ == "__main__":
    print("Starting GPS background thread...")
    t = threading.Thread(target=update_gps_loop, daemon=True)
    t.start()

    print("\n========================================")
    print("  GPS Server running on port 5000")
    print("  Pi should fetch: http://<this-phone-ip>:5000/gps")
    print("  Check fix:       http://<this-phone-ip>:5000/health")
    print("========================================\n")

    app.run(host="0.0.0.0", port=5000)