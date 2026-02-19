"""
Background service that watches the upload queue directory
and sends batches to the cloud backend when internet is available.
"""

import os
import json
import time
import threading
import requests


class CloudUploader:

    def __init__(self, api_url, queue_dir="logs/queue", device_id="pi5-001"):
        self.api_url = api_url.rstrip("/")
        self.queue_dir = queue_dir
        self.device_id = device_id
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._upload_loop, daemon=True)
        self._thread.start()
        print(f"[Uploader] Watching {self.queue_dir} → {self.api_url}")

    def _upload_loop(self):
        while self._running:
            batch_files = sorted([
                f for f in os.listdir(self.queue_dir) if f.endswith(".json")
            ])

            for fname in batch_files:
                path = os.path.join(self.queue_dir, fname)
                try:
                    with open(path, "r") as f:
                        detections = json.load(f)

                    resp = requests.post(
                        f"{self.api_url}/api/detections/batch",
                        json={
                            "device_id": self.device_id,
                            "detections": detections,
                        },
                        timeout=10,
                    )

                    if resp.status_code in (200, 201):
                        os.remove(path)
                        print(f"[Uploader] Uploaded {fname} ({len(detections)} detections)")
                    else:
                        print(f"[Uploader] Server returned {resp.status_code}, will retry")

                except requests.RequestException:
                    # No internet — that's fine, we'll retry next cycle
                    break
                except Exception as e:
                    print(f"[Uploader] Error: {e}")

            # Check every 30 seconds
            time.sleep(30)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)