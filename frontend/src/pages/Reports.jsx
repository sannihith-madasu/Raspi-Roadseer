import { useMemo } from "react";
import { FileText, Download, AlertTriangle, MapPin, Calendar } from "lucide-react";
import { getMockData } from "../data/mockPotholes";

export default function Reports() {
  const data = useMemo(() => getMockData(), []);

  // Group by ward
  const wardReports = useMemo(() => {
    const grouped = {};
    data.forEach((d) => {
      if (!grouped[d.ward]) {
        grouped[d.ward] = { ward: d.ward, potholes: [], totalReports: 0, worstSeverity: 0 };
      }
      grouped[d.ward].potholes.push(d);
      grouped[d.ward].totalReports += d.report_count;
      grouped[d.ward].worstSeverity = Math.max(grouped[d.ward].worstSeverity, d.severity_score);
    });
    return Object.values(grouped).sort((a, b) => b.worstSeverity - a.worstSeverity);
  }, [data]);

  const handleExportCSV = (ward) => {
    const potholes = wardReports.find(w => w.ward === ward)?.potholes || [];
    const headers = "ID,Latitude,Longitude,Class,Severity,Reports,Road,First Reported\n";
    const rows = potholes.map(p =>
      `${p.id},${p.latitude},${p.longitude},${p.class_name},${p.severity_score},${p.report_count},${p.road_name},${p.first_reported}`
    ).join("\n");
    const blob = new Blob([headers + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `roadseer_report_${ward.replace(/\s/g, "_")}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen pt-16">
      <div className="mx-auto max-w-5xl px-4 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Municipal Reports</h1>
            <p className="mt-1 text-slate-500">Ward-wise priority reports for road maintenance</p>
          </div>
          <div className="flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2 text-sm text-slate-400">
            <Calendar className="h-4 w-4" />
            Generated: {new Date().toLocaleDateString("en-IN")}
          </div>
        </div>

        <div className="space-y-4">
          {wardReports.map((ward) => {
            const critical = ward.potholes.filter(p => p.status === "critical").length;
            const moderate = ward.potholes.filter(p => p.status === "moderate").length;

            return (
              <div key={ward.ward} className="rounded-2xl border border-slate-800 bg-slate-900/50 overflow-hidden">
                <div className="flex items-center justify-between p-5">
                  <div className="flex items-center gap-4">
                    <div className={`rounded-xl p-3 ${
                      ward.worstSeverity >= 7 ? "bg-red-500/15 text-red-400" :
                      ward.worstSeverity >= 4 ? "bg-amber-500/15 text-amber-400" :
                      "bg-green-500/15 text-green-400"
                    }`}>
                      <MapPin className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold">{ward.ward}</h3>
                      <div className="mt-0.5 flex gap-3 text-xs text-slate-500">
                        <span>{ward.potholes.length} detections</span>
                        <span>•</span>
                        <span>{ward.totalReports} total reports</span>
                        <span>•</span>
                        <span className="text-red-400">{critical} critical</span>
                        <span>•</span>
                        <span className="text-amber-400">{moderate} moderate</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-sm text-slate-500">Priority</div>
                      <div className={`text-xl font-bold ${
                        ward.worstSeverity >= 7 ? "text-red-400" :
                        ward.worstSeverity >= 4 ? "text-amber-400" : "text-green-400"
                      }`}>
                        {ward.worstSeverity.toFixed(1)}
                      </div>
                    </div>
                    <button
                      onClick={() => handleExportCSV(ward.ward)}
                      className="rounded-lg border border-slate-700 p-2 text-slate-400 transition-colors hover:border-orange-500 hover:text-orange-400"
                      title="Download CSV report"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Top 3 worst potholes in this ward */}
                <div className="border-t border-slate-800 bg-slate-950/50 px-5 py-3">
                  <div className="text-xs font-medium text-slate-600 mb-2">TOP PRIORITY IN THIS WARD</div>
                  <div className="grid gap-2 sm:grid-cols-3">
                    {ward.potholes
                      .sort((a, b) => b.severity_score - a.severity_score)
                      .slice(0, 3)
                      .map((p) => (
                        <div key={p.id} className="flex items-center justify-between rounded-lg bg-slate-900 px-3 py-2 text-xs">
                          <div>
                            <span className="text-slate-400">{p.road_name}</span>
                            <span className="ml-2 capitalize text-slate-600">({p.class_name})</span>
                          </div>
                          <span className={`font-bold ${
                            p.severity_score >= 7 ? "text-red-400" : "text-amber-400"
                          }`}>
                            {p.severity_score}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}