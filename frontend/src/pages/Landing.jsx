import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Map, Users, Shield, Cpu, Radio, TrendingUp } from "lucide-react";
import { getMockStats } from "../data/api";
import { useApi } from "../hooks/useApi";

const features = [
  {
    icon: Cpu,
    title: "Edge AI on Raspberry Pi",
    desc: "YOLO26n with INT8 quantization runs at 15 FPS on a Raspberry Pi 5. No cloud needed for detection.",
  },
  {
    icon: Map,
    title: "GPS-Tagged Detections",
    desc: "Every pothole is geotagged with coordinates, severity score, and timestamp. Automatic deduplication across devices.",
  },
  {
    icon: Users,
    title: "Crowdsourced Intelligence",
    desc: "Deploy on auto-rickshaws, buses, delivery bikes. More devices = complete road quality map within days.",
  },
  {
    icon: Shield,
    title: "Municipal Reports",
    desc: "Ward-wise priority reports generated automatically. Municipalities fix the worst roads first.",
  },
  {
    icon: Radio,
    title: "Offline-First",
    desc: "Logs locally when there's no connectivity. Syncs automatically when back online. Built for Indian roads.",
  },
  {
    icon: TrendingUp,
    title: "Trend Tracking",
    desc: "Track which potholes persist over weeks. Hold municipalities accountable with data.",
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.5 },
  }),
};

export default function Landing() {
  // ── ALL HOOKS FIRST ──
  const { data: stats, loading } = useApi(getMockStats);

  // ── Loading check AFTER all hooks ──
  if (loading || !stats)
    return <div className="flex h-screen items-center justify-center text-slate-500">Loading...</div>;

  return (
    <div className="pt-16">
      {/* Hero */}
      <section className="relative overflow-hidden">
        {/* Grid background */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(249,115,22,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(249,115,22,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />

        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:py-32">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-orange-500/30 bg-orange-500/10 px-4 py-1.5 text-sm text-orange-400">
              <Cpu className="h-3.5 w-3.5" />
              Powered by Arm Cortex-A76 • Raspberry Pi 5
            </div>

            <h1 className="mx-auto max-w-4xl text-5xl font-bold leading-tight tracking-tight sm:text-7xl">
              Every Road Tells
              <br />
              <span className="bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent">
                a Story
              </span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
              Real-time pothole detection from dashcam footage on Raspberry Pi.
              Crowdsource road quality data. Help municipalities fix roads that matter most.
            </p>

            <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
              <Link
                to="/map"
                className="inline-flex items-center gap-2 rounded-xl bg-orange-500 px-6 py-3 font-semibold text-white transition-colors hover:bg-orange-600"
              >
                View Live Map <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl border border-slate-700 px-6 py-3 font-semibold text-slate-300 transition-colors hover:border-slate-600 hover:text-white"
              >
                Analytics Dashboard
              </Link>
            </div>
          </motion.div>

          {/* Quick stats */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="mx-auto mt-20 grid max-w-4xl grid-cols-2 gap-4 sm:grid-cols-4"
          >
            {[
              { value: stats.total_detections, label: "Potholes Detected" },
              { value: stats.active_devices, label: "Active Devices" },
              { value: stats.wards_affected, label: "Wards Mapped" },
              { value: stats.avg_severity + "/10", label: "Avg Severity" },
            ].map(({ value, label }) => (
              <div key={label} className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 text-center">
                <div className="text-3xl font-bold text-orange-400">{value}</div>
                <div className="mt-1 text-sm text-slate-500">{label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-slate-800 bg-slate-900/30">
        <div className="mx-auto max-w-7xl px-4 py-24">
          <div className="text-center">
            <h2 className="text-3xl font-bold sm:text-4xl">How It Works</h2>
            <p className="mt-3 text-slate-400">From dashcam to municipal action — fully automated</p>
          </div>

          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeUp}
                className="group rounded-2xl border border-slate-800 bg-slate-900/50 p-6 transition-colors hover:border-orange-500/30"
              >
                <div className="mb-4 inline-flex rounded-xl bg-orange-500/10 p-3 text-orange-400 transition-colors group-hover:bg-orange-500/20">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline diagram */}
      <section className="border-t border-slate-800">
        <div className="mx-auto max-w-7xl px-4 py-24 text-center">
          <h2 className="text-3xl font-bold">Detection Pipeline</h2>
          <div className="mx-auto mt-12 flex max-w-5xl flex-wrap items-center justify-center gap-3">
            {[
              "📷 Dashcam",
              "→",
              "🧠 YOLO26n (INT8)",
              "→",
              "📍 GPS Tag",
              "→",
              "📤 Upload",
              "→",
              "🗺️ Heatmap",
              "→",
              "📋 Municipal Report",
            ].map((step, i) =>
              step === "→" ? (
                <ArrowRight key={i} className="h-5 w-5 text-slate-600" />
              ) : (
                <div key={i} className="rounded-xl border border-slate-800 bg-slate-900 px-4 py-2 text-sm">
                  {step}
                </div>
              )
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 text-center text-sm text-slate-600">
        © 2026 Raspi-Roadseer | Advancing Road Safety with Edge AI
      </footer>
    </div>
  );
}