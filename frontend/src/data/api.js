/**
 * Real API client — replaces mockPotholes.js
 *
 * Same function names and return shapes,
 * so your components don't need ANY changes.
 */

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function getMockData() {
  const res = await fetch(`${API_BASE}/api/detections`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const detections = await res.json();

  // Map backend shape → frontend shape (exact same fields as mockPotholes.js)
  return detections.map((d) => ({
    id: `PH-${d.id}`,
    latitude: d.latitude,
    longitude: d.longitude,
    class_name: d.class_name,
    confidence: d.avg_confidence,
    severity_score: d.severity_score,
    report_count: d.report_count,
    first_reported: d.first_reported,
    last_reported: d.last_reported,
    status:
      d.severity_score >= 7
        ? "critical"
        : d.severity_score >= 4
        ? "moderate"
        : "low",
    ward: d.ward || "Unknown",
    road_name: d.road_name || "Unnamed Road",
    device_ids: [],
    speed_at_detection: d.avg_speed_kmh,
  }));
}

export async function getMockStats() {
  const res = await fetch(`${API_BASE}/api/stats`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getWardReports() {
  const res = await fetch(`${API_BASE}/api/reports`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const reports = await res.json();

  // Map top_potholes to frontend shape
  return reports.map((r) => ({
    ...r,
    top_potholes: r.top_potholes.map((d) => ({
      id: `PH-${d.id}`,
      latitude: d.latitude,
      longitude: d.longitude,
      class_name: d.class_name,
      confidence: d.avg_confidence,
      severity_score: d.severity_score,
      report_count: d.report_count,
      first_reported: d.first_reported,
      last_reported: d.last_reported,
      status:
        d.severity_score >= 7
          ? "critical"
          : d.severity_score >= 4
          ? "moderate"
          : "low",
      ward: d.ward || "Unknown",
      road_name: d.road_name || "Unnamed Road",
      device_ids: [],
      speed_at_detection: d.avg_speed_kmh,
    })),
  }));
}

export async function resolveDetection(id) {
  const numericId = id.replace("PH-", "");
  const res = await fetch(
    `${API_BASE}/api/detections/${numericId}/resolve`,
    { method: "PATCH" }
  );
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}