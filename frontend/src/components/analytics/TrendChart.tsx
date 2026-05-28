"use client";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
} from "recharts";

export interface TrendPoint {
  session_id: number;
  label: string;
  overall: number;
  technical?: number | null;
  communication?: number | null;
  confidence?: number | null;
  engagement?: number | null;
  company?: string | null;
  role?: string | null;
}

export function TrendChart({ points }: { points: TrendPoint[] }) {
  if (points.length === 0) {
    return (
      <div className="h-[260px] flex items-center justify-center text-slate-400 text-sm">
        Complete an interview to start seeing your trend.
      </div>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={points} margin={{ top: 10, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" vertical={false} />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} stroke="#94a3b8" />
        <YAxis domain={[0, 10]} tick={{ fontSize: 11 }} stroke="#94a3b8" />
        <Tooltip
          contentStyle={{ borderRadius: 8, fontSize: 12, border: "1px solid #e2e8f0" }}
          formatter={(v: any) => [Number(v).toFixed(2), undefined]}
          labelFormatter={(l, items: any) => {
            const p = items?.[0]?.payload;
            return p?.company ? `${l} · ${p.company}` : l;
          }}
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line
          type="monotone"
          dataKey="overall"
          name="Overall"
          stroke="#2745f5"
          strokeWidth={2.5}
          dot={{ r: 3 }}
        />
        <Line type="monotone" dataKey="technical"     name="Technical"     stroke="#10b981" strokeWidth={1.5} dot={false} />
        <Line type="monotone" dataKey="communication" name="Communication" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
        <Line type="monotone" dataKey="confidence"    name="Confidence"    stroke="#8b5cf6" strokeWidth={1.5} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
