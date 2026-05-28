"use client";
import { motion } from "framer-motion";

interface Summary {
  technical: number;
  communication: number;
  confidence: number;
  engagement: number;
}

const DIMS: { key: keyof Summary; label: string }[] = [
  { key: "technical",     label: "Technical accuracy" },
  { key: "communication", label: "Communication clarity" },
  { key: "confidence",    label: "Confidence" },
  { key: "engagement",    label: "Engagement" },
];

export function ScoreBars({ summary }: { summary: Summary }) {
  return (
    <div className="space-y-4">
      {DIMS.map((d, i) => {
        const v = summary[d.key] ?? 0;
        const pct = Math.max(0, Math.min(100, (v / 10) * 100));
        const color =
          pct >= 75 ? "bg-green-500"
          : pct >= 50 ? "bg-brand-500"
          : pct >= 30 ? "bg-amber-500"
          : "bg-red-500";

        return (
          <div key={d.key}>
            <div className="flex justify-between text-sm mb-1.5">
              <span className="text-slate-700">{d.label}</span>
              <span className="font-semibold tabular-nums">{v.toFixed(1)} / 10</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <motion.div
                className={`h-full ${color}`}
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ delay: i * 0.1, duration: 0.8, ease: "easeOut" }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
