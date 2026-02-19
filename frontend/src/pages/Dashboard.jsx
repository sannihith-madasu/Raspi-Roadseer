import { useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid,
} from "recharts";
import { AlertTriangle, MapPin, Cpu, TrendingUp, Activity, Users } from "lucide-react";
import { getMockData, getMockStats } from "../data/api";
import { useApi } from "../hooks/useApi";

const COLORS = { critical: "#ef4444", moderate: "#f59e0b", low: "#22c55e" };

function StatCard({ icon: Icon, label, value, sub, color = "text-orange-400" }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-slate-800 p-2.5">
          <Icon className={`h-5 w-5 ${color}`} />
        </div>
        <div>
          <div className={`text-2xl font-bold ${color}`}>{value}</div>
          <div className="text-sm text-slate-500">{label}</div>
          {sub && <div className="text-xs text-slate-600">{sub}</div>}
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  // ── ALL HOOKS FIRST ──
  const { data, loading: loadingData } = useApi(getMockData);
  const { data: stats, loading: loadingStats } = useApi(getMockStats);

  // Ward breakdown
  const wardData = useMemo(() => {
    if (!data) return [];
    const counts = {};
    data.forEach((d) => {
      counts[d.ward] = counts[d.ward] || { ward: d.ward, critical: 0, moderate: 0, low: 0 };
      counts[d.ward][d.status]++;
    });
    return Object.values(counts).sort((a, b) => (b.critical + b.moderate + b.low) - (a.critical + a.moderate + a.low));
  }, [data]);

  // Severity distribution for pie chart
  const severityPie = useMemo(() => {
    if (!stats) return [];
    return [
      { name: "Critical", value: stats.critical_count, color: COLORS.critical },
      { name: "Moderate", value: stats.moderate_count, color: COLORS.moderate },
      { name: "Low", value: stats.low_count, color: COLORS.low },
    ];
  }, [stats]);

  // Fake daily trend (last 14 days)
  const dailyTrend = useMemo(() => {
    return Array.from({ length: 14 }, (_, i) => {
      const date = new Date(Date.now() - (13 - i) * 86400000);
      return {
        date: date.toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
        detections: Math.floor(Math.random() * 20 + 5),
        resolved: Math.floor(Math.random() * 8),
      };
    });
  }, []);

  // ── Loading check AFTER all hooks ──
  if (loadingData || loadingStats || !data || !stats)
    return <div className="flex h-screen items-center justify-center text-slate-500">Loading...</div>;

  return (
    <div className="min-h-screen pt-16">
      <div className="mx-auto max-w-7xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="mt-1 text-slate-500">Crowdsourced road quality intelligence</p>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <StatCard icon={AlertTriangle} label="Total Detected" value={stats.total_detections} color="text-orange-400" />
          <StatCard icon={AlertTriangle} label="Critical" value={stats.critical_count} color="text-red-400" />
          <StatCard icon={MapPin} label="Wards Affected" value={stats.wards_affected} color="text-blue-400" />
          <StatCard icon={Cpu} label="Active Devices" value={stats.active_devices} color="text-green-400" />
          <StatCard icon={Users} label="Total Reports" value={stats.total_reports} color="text-purple-400" />
          <StatCard icon={Activity} label="Avg Severity" value={`${stats.avg_severity}/10`} color="text-amber-400" />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          {/* Ward breakdown bar chart */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 lg:col-span-2">
            <h3 className="mb-4 text-lg font-semibold">Detections by Ward</h3>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={wardData} layout="vertical">
                <XAxis type="number" stroke="#475569" fontSize={12} />
                <YAxis type="category" dataKey="ward" width={120} stroke="#475569" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }}
                  labelStyle={{ color: "#f8fafc" }}
                />
                <Bar dataKey="critical" stackId="a" fill={COLORS.critical} radius={[0, 0, 0, 0]} />
                <Bar dataKey="moderate" stackId="a" fill={COLORS.moderate} />
                <Bar dataKey="low" stackId="a" fill={COLORS.low} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Severity pie */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
            <h3 className="mb-4 text-lg font-semibold">Severity Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={severityPie}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {severityPie.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 flex justify-center gap-4">
              {severityPie.map(({ name, value, color }) => (
                <div key={name} className="flex items-center gap-1.5">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
                  <span className="text-xs text-slate-400">{name} ({value})</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Daily trend line chart */}
        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
          <h3 className="mb-4 text-lg font-semibold">Detection Trend (Last 14 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dailyTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#475569" fontSize={12} />
              <YAxis stroke="#475569" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }}
                labelStyle={{ color: "#f8fafc" }}
              />
              <Line type="monotone" dataKey="detections" stroke="#f97316" strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="resolved" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-3 flex gap-6 justify-center">
            <div className="flex items-center gap-2">
              <span className="h-0.5 w-5 bg-orange-500 rounded" />
              <span className="text-xs text-slate-400">New Detections</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-0.5 w-5 bg-green-500 rounded" />
              <span className="text-xs text-slate-400">Resolved</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}