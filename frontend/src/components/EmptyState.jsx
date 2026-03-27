import React from "react";
import { RotateCcw } from "lucide-react";

export default function EmptyState({
  title = "No data yet",
  description = "Once the first detections are uploaded, analytics will appear here automatically.",
  action = null, // optional JSX button/link
  icon: Icon = RotateCcw, // allow overriding per page if you want
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-10">
      <div className="mx-auto flex max-w-xl flex-col items-center text-center">
        {/* Icon badge */}
        <div className="mb-4 inline-flex items-center justify-center rounded-2xl border border-slate-700 bg-slate-950/60 p-4">
          <div className="rounded-xl bg-gradient-to-br from-orange-500/20 to-red-500/10 p-3">
            <Icon className="h-7 w-7 text-orange-300" />
          </div>
        </div>

        <h3 className="text-xl font-semibold text-slate-100">{title}</h3>
        <p className="mt-2 text-sm leading-relaxed text-slate-400">{description}</p>

        {action ? <div className="mt-5">{action}</div> : null}

        <div className="mt-6 text-xs text-slate-600">
          Tip: keep the Pi pipeline running and ensure the backend is reachable.
        </div>
      </div>
    </div>
  );
}