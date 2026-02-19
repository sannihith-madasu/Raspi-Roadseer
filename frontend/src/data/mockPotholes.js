/**
 * Mock pothole detection data.
 * Shape matches what your Pi will actually send via API.
 * When backend is ready, replace this with fetch() calls.
 */

// Hyderabad coordinates (adjust to your city)
const CITY_CENTER = { lat: 17.385, lng: 78.4867 };

const WARD_NAMES = [
  "Jubilee Hills", "Banjara Hills", "Madhapur", "Gachibowli",
  "Kukatpally", "Ameerpet", "Secunderabad", "Begumpet",
  "Kondapur", "Miyapur", "Dilsukhnagar", "LB Nagar",
];

const ROAD_NAMES = [
  "Road No. 36", "Tank Bund Road", "Necklace Road", "ORR Exit 5",
  "Hitech City Main Road", "Biodiversity Junction", "Cyber Towers Road",
  "JNTU-Kukatpally Road", "Panjagutta Circle", "Tolichowki Main Road",
  "Mehdipatnam-Rethibowli Road", "Attapur Road", "Aramghar-Shamshabad Road",
];

function randomInRange(center, rangeKm) {
  // ~0.009 degrees ≈ 1km
  const offset = rangeKm * 0.009;
  return center + (Math.random() - 0.5) * 2 * offset;
}

function generateId() {
  return `PH-${Date.now().toString(36)}-${Math.random().toString(36).substr(2, 5)}`.toUpperCase();
}

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function generateMockDetection(id = null) {
  const severity = Math.round((Math.random() * 7 + 2.5) * 10) / 10; // 2.5 - 9.5
  const confidence = Math.round((Math.random() * 0.35 + 0.55) * 100) / 100; // 0.55 - 0.90
  const className = Math.random() > 0.2 ? "pothole" : "barricade";
  const reportCount = Math.floor(Math.random() * 40) + 1;

  const daysAgo = Math.floor(Math.random() * 30);
  const timestamp = new Date(Date.now() - daysAgo * 86400000).toISOString();

  return {
    id: id || generateId(),
    latitude: randomInRange(CITY_CENTER.lat, 8),
    longitude: randomInRange(CITY_CENTER.lng, 8),
    class_name: className,
    confidence,
    severity_score: severity,
    report_count: reportCount,
    first_reported: timestamp,
    last_reported: new Date(
      Date.now() - Math.floor(Math.random() * daysAgo) * 86400000
    ).toISOString(),
    status: severity > 7 ? "critical" : severity > 4 ? "moderate" : "low",
    ward: randomChoice(WARD_NAMES),
    road_name: randomChoice(ROAD_NAMES),
    device_ids: Array.from(
      { length: Math.min(reportCount, 5) },
      (_, i) => `PI5-${String(i + 1).padStart(3, "0")}`
    ),
    speed_at_detection: Math.round(Math.random() * 40 + 10), // 10-50 kmh
  };
}

export function generateMockDataset(count = 150) {
  return Array.from({ length: count }, () => generateMockDetection());
}

// Pre-generated dataset — stable across renders
let _cached = null;
export function getMockData() {
  if (!_cached) {
    _cached = generateMockDataset(150);
  }
  return _cached;
}

// Stats derived from data
export function getMockStats(data = null) {
  const d = data || getMockData();
  const critical = d.filter(p => p.status === "critical").length;
  const moderate = d.filter(p => p.status === "moderate").length;
  const potholes = d.filter(p => p.class_name === "pothole").length;
  const totalReports = d.reduce((sum, p) => sum + p.report_count, 0);

  return {
    total_detections: d.length,
    critical_count: critical,
    moderate_count: moderate,
    low_count: d.length - critical - moderate,
    pothole_count: potholes,
    barricade_count: d.length - potholes,
    total_reports: totalReports,
    active_devices: new Set(d.flatMap(p => p.device_ids)).size,
    avg_severity: Math.round((d.reduce((s, p) => s + p.severity_score, 0) / d.length) * 10) / 10,
    wards_affected: new Set(d.map(p => p.ward)).size,
  };
}