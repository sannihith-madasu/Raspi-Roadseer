"""
Reads GPS data from the phone's HTTP server.
Drop-in replacement for the hardware GPS reader.
Same interface: .start(), .get_location(), .stop()
"""

import requests
import threading
import time


class PhoneGPSReader:
    """
    Polls your phone's GPS server over WiFi.
    Phone runs phone_gps_server.py on Termux.
    """

    def __init__(self, phone_ip="192.168.1.42", port=5000, poll_interval=1.0):
        self.url = f"http://{phone_ip}:{port}/gps"
        self.poll_interval = poll_interval
        self.current_data = {
            "lat": 0.0,
            "lon": 0.0,
            "speed_kmh": 0.0,
            "altitude": 0.0,
            "accuracy": 0.0,
            "bearing": 0.0,
            "fix": False,
        }
        self._running = False
        self._thread = None
        self._consecutive_failures = 0

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        print(f"[GPS] Polling phone at {self.url}")

    def _poll_loop(self):
        while self._running:
            try:
                resp = requests.get(self.url, timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    self.current_data = {
                        "lat": data.get("latitude", 0.0),
                        "lon": data.get("longitude", 0.0),
                        "speed_kmh": data.get("speed", 0.0) * 3.6,  # m/s → km/h
                        "altitude": data.get("altitude", 0.0),
                        "accuracy": data.get("accuracy", 0.0),
                        "bearing": data.get("bearing", 0.0),
                        "fix": data.get("fix", False),
                    }
                    self._consecutive_failures = 0
                else:
                    self._consecutive_failures += 1

            except requests.RequestException:
                self._consecutive_failures += 1
                if self._consecutive_failures <= 3:
                    print(f"[GPS] Phone unreachable (attempt {self._consecutive_failures})")
                self.current_data["fix"] = False

            time.sleep(self.poll_interval)

    def get_location(self):
        """Returns location dict if we have a fix, else None."""
        if self.current_data["fix"]:
            return self.current_data
        return None

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        print("[GPS] Stopped.")