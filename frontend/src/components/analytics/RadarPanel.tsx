"use client";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

interface DimMap {
  technical: number;
  communication: number;
  confidence: number;
  engagement: number;
}

export function RadarPanel({
  latest,
  average,
}: {
  latest: DimMap | null;
  average: DimMap | null;
}) {
  if (!latest || !average) {
    return (
      <div className="h-[260px] flex items-center justify-center text-slate-400 text-sm">
        Complete a session to see your dimension breakdown.
      </div>
    );
  }
  const data = (
    ["technical", "communication", "confidence", "engagement"] as const
  ).map((k) => ({
    dim: k.charAt(0).toUpperCase() + k.slice(1),
    "Your latest": Number(latest[k] ?? 0),
    "Your average": Number(average[k] ?? 0),
  }));
  return (
    <ResponsiveContainer width="100%" height={260}>
      <RadarChart data={data}>
        <PolarGrid stroke="#e2e8f0" />
        <PolarAngleAxis dataKey="dim" tick={{ fontSize: 11 }} />
        <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fontSize: 10 }} />
        <Radar
          name="Your latest"
          dataKey="Your latest"
          stroke="#2745f5"
          fill="#2745f5"
          fillOpacity={0.25}
        />
        <Radar
          name="Your average"
          dataKey="Your average"
          stroke="#94a3b8"
          fill="#94a3b8"
          fillOpacity={0.15}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{ borderRadius: 8, fontSize: 12, border: "1px solid #e2e8f0" }}
          formatter={(v: any) => Number(v).toFixed(2)}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
