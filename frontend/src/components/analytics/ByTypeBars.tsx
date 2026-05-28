"use client";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface Item { type: string; count: number; average: number | null }

export function ByTypeBars({ items }: { items: Item[] }) {
  if (items.length === 0) {
    return (
      <div className="h-[220px] flex items-center justify-center text-slate-400 text-sm">
        No completed sessions yet.
      </div>
    );
  }
  const data = items.map((i) => ({
    type: i.type.charAt(0).toUpperCase() + i.type.slice(1),
    Average: i.average ?? 0,
    Sessions: i.count,
  }));
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 5, right: 8, left: -8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" vertical={false} />
        <XAxis dataKey="type" tick={{ fontSize: 12 }} stroke="#94a3b8" />
        <YAxis tick={{ fontSize: 11 }} stroke="#94a3b8" domain={[0, 10]} />
        <Tooltip
          contentStyle={{ borderRadius: 8, fontSize: 12, border: "1px solid #e2e8f0" }}
        />
        <Bar dataKey="Average" fill="#3a64ff" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
