import { useState, useMemo } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import { Search } from "lucide-react";
import { getMockData, getMockStats } from "../data/api";
import { useApi } from "../hooks/useApi";
import EmptyState from "../components/EmptyState";

// Severity → color
function severityColor(score) {
  if (score >= 7) return "#ef4444"; // red
  if (score >= 4) return "#f59e0b"; // amber
  return "#22c55e"; // green
}

function severityLabel(score) {
  if (score >= 7) return "Critical";
  if (score >= 4) return "Moderate";
  return "Low";
}

function MapUpdater({ center }) {
  const map = useMap();
  map.setView(center, map.getZoom());
  return null;
}

export default function MapView() {
  // ── ALL HOOKS FIRST ──
  const { data: allData, loading: loadingData } = useApi(getMockData);
  const { data: stats, loading: loadingStats } = useApi(getMockStats);

  const [filters, setFilters] = useState({
    severity: "all",
    classType: "all",
    search: "",
  });
  const [selectedDetection, setSelectedDetection] = useState(null);

  const filtered = useMemo(() => {
    if (!allData) return [];
    return allData.filter((d) => {
      if (filters.severity !== "all" && d.status !== filters.severity) return false;
      if (filters.classType !== "all" && d.class_name !== filters.classType) return false;
      if (filters.search) {
        const q = filters.search.toLowerCase();
        return (
          d.road_name.toLowerCase().includes(q) ||
          d.ward.toLowerCase().includes(q) ||
          d.id.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [allData, filters]);

  const center = [17.385, 78.4867];

  // ── Loading check AFTER all hooks ──
  if (loadingData || loadingStats || !allData || !stats) {
    return <div className="flex h-screen items-center justify-center text-slate-500">Loading...</div>;
  }

  const hasListData = filtered.length > 0;

  return (
    <div className="flex h-screen pt-16">
      {/* Sidebar */}
      <div className="flex w-80 flex-col border-r border-slate-800 bg-slate-950 lg:w-96">
        {/* Stats bar */}
        <div className="grid grid-cols-3 gap-px border-b border-slate-800 bg-slate-800">
          {[
            { label: "Total", value: filtered.length, color: "text-white" },
            { label: "Critical", value: filtered.filter((d) => d.status === "critical").length, color: "text-red-400" },
            { label: "Devices", value: stats.active_devices, color: "text-green-400" },
          ].map(({ label, value, color }) => (
            <div key={label} className="bg-slate-900 p-3 text-center">
              <div className={`text-lg font-bold ${color}`}>{value}</div>
              <div className="text-xs text-slate-500">{label}</div>
            </div>
          ))}
        </div>

        {/* Search + Filters */}
        <div className="border-b border-slate-800 p-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search road, ward, ID..."
              value={filters.search}
              onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-2 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none focus:border-orange-500"
            />
          </div>

          {/* Severity filter */}
          <div className="mt-3 flex gap-2">
            {["all", "critical", "moderate", "low"].map((s) => (
              <button
                key={s}
                onClick={() => setFilters((f) => ({ ...f, severity: s }))}
                className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors ${
                  filters.severity === s
                    ? "bg-orange-500 text-white"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Class filter */}
          <div className="mt-2 flex gap-2">
            {["all", "pothole", "barricade"].map((c) => (
              <button
                key={c}
                onClick={() => setFilters((f) => ({ ...f, classType: c }))}
                className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors ${
                  filters.classType === c
                    ? "bg-orange-500 text-white"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Detection list */}
        <div className="flex-1 overflow-y-auto p-3">
          {!hasListData ? (
            <EmptyState
              title="No detections match your filters"
              description="Try clearing filters or wait for the first uploads from the Raspberry Pi. When data arrives, it will show up here automatically."
            />
          ) : (
            <div className="space-y-2">
              {filtered.map((d) => (
                <button
                  key={d.id}
                  onClick={() => setSelectedDetection(d)}
                  className={`w-full rounded-xl border border-slate-800/60 bg-slate-900/30 p-4 text-left transition-colors hover:bg-slate-900 ${
                    selectedDetection?.id === d.id ? "border-orange-500/60 ring-1 ring-orange-500/30" : ""
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span
                          className="inline-block h-2.5 w-2.5 rounded-full"
                          style={{ backgroundColor: severityColor(d.severity_score) }}
                        />
                        <span className="text-sm font-medium capitalize text-slate-100">{d.class_name}</span>
                      </div>
                      <div className="mt-1 text-xs text-slate-400">{d.road_name}</div>
                      <div className="text-xs text-slate-600">{d.ward}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold" style={{ color: severityColor(d.severity_score) }}>
                        {d.severity_score}
                      </div>
                      <div className="text-xs text-slate-600">{d.report_count} reports</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Map */}
      <div className="relative flex-1">
        <MapContainer center={center} zoom={12} className="h-full w-full" zoomControl={false}>
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          <MapUpdater center={center} />

          {filtered.map((d) => (
            <CircleMarker
              key={d.id}
              center={[d.latitude, d.longitude]}
              radius={Math.max(5, d.severity_score * 1.2)}
              pathOptions={{
                color: severityColor(d.severity_score),
                fillColor: severityColor(d.severity_score),
                fillOpacity: 0.6,
                weight: selectedDetection?.id === d.id ? 3 : 1,
              }}
              eventHandlers={{
                click: () => setSelectedDetection(d),
              }}
            >
              <Popup>
                <div className="min-w-48 text-slate-900">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-bold capitalize">{d.class_name}</span>
                    <span
                      className="rounded-full px-2 py-0.5 text-xs font-medium text-white"
                      style={{ backgroundColor: severityColor(d.severity_score) }}
                    >
                      {severityLabel(d.severity_score)}
                    </span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <p>
                      <strong>Road:</strong> {d.road_name}
                    </p>
                    <p>
                      <strong>Ward:</strong> {d.ward}
                    </p>
                    <p>
                      <strong>Severity:</strong> {d.severity_score}/10
                    </p>
                    <p>
                      <strong>Confidence:</strong> {(d.confidence * 100).toFixed(0)}%
                    </p>
                    <p>
                      <strong>Reports:</strong> {d.report_count}
                    </p>
                    <p>
                      <strong>First seen:</strong> {new Date(d.first_reported).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>

        {/* Map legend */}
        <div className="absolute bottom-6 right-6 rounded-xl border border-slate-700 bg-slate-900/90 p-4 backdrop-blur">
          <div className="mb-2 text-xs font-semibold text-slate-400">SEVERITY</div>
          {[
            { color: "#ef4444", label: "Critical (7-10)" },
            { color: "#f59e0b", label: "Moderate (4-6.9)" },
            { color: "#22c55e", label: "Low (1-3.9)" },
          ].map(({ color, label }) => (
            <div key={label} className="mt-1 flex items-center gap-2">
              <span className="h-3 w-3 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-xs text-slate-400">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}