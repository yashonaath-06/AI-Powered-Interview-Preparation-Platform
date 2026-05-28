"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { TrendingUp, Award, Activity, AlertTriangle, GitCompare } from "lucide-react";

import { api } from "@/lib/api";
import { Card, CardDescription, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { TrendChart } from "@/components/analytics/TrendChart";
import { RadarPanel } from "@/components/analytics/RadarPanel";
import { ByTypeBars } from "@/components/analytics/ByTypeBars";
import { CompareDialog, SessionLite } from "@/components/analytics/CompareDialog";

interface Summary {
  total_sessions: number;
  completed_sessions: number;
  average_score: number | null;
  best_score: number | null;
  latest_score: number | null;
  growth_pct: number | null;
}

export default function AnalyticsPage() {
  const [compareOpen, setCompareOpen] = useState(false);

  const summary  = useQuery<Summary>({ queryKey: ["a-summary"],   queryFn: async () => (await api.get("/api/analytics/summary")).data });
  const trend    = useQuery<any>({     queryKey: ["a-trend"],     queryFn: async () => (await api.get("/api/analytics/trend")).data });
  const byType   = useQuery<any>({     queryKey: ["a-bytype"],    queryFn: async () => (await api.get("/api/analytics/by-type")).data });
  const dims     = useQuery<any>({     queryKey: ["a-dims"],      queryFn: async () => (await api.get("/api/analytics/dimensions")).data });
  const weak     = useQuery<any>({     queryKey: ["a-weak"],      queryFn: async () => (await api.get("/api/analytics/weaknesses")).data });
  const sessions = useQuery<SessionLite[]>({ queryKey: ["a-sessions"], queryFn: async () => (await api.get("/api/interviews")).data });

  const completedSessions = (sessions.data || []).filter(
    (s) => s.overall_score != null,
  );

  return (
    <div className="p-6 lg:p-10 max-w-6xl mx-auto">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Performance Analytics</h1>
          <p className="text-slate-500 text-sm mt-1">
            Track how you&apos;re improving across all your mock interviews.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          disabled={completedSessions.length < 2}
          onClick={() => setCompareOpen(true)}
        >
          <GitCompare size={14} /> Compare sessions
        </Button>
      </header>

      {/* Stat cards */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat label="Average score" icon={Activity}
              value={fmt(summary.data?.average_score)} suffix="/10" />
        <Stat label="Best score" icon={Award}
              value={fmt(summary.data?.best_score)} suffix="/10" tone="green" />
        <Stat label="Latest score" icon={TrendingUp}
              value={fmt(summary.data?.latest_score)} suffix="/10" />
        <Stat label="Growth" icon={TrendingUp}
              value={summary.data?.growth_pct != null ? (summary.data.growth_pct >= 0 ? `+${summary.data.growth_pct}` : `${summary.data.growth_pct}`) : "—"}
              suffix={summary.data?.growth_pct != null ? "%" : ""}
              tone={(summary.data?.growth_pct ?? 0) >= 0 ? "green" : "amber"} />
      </section>

      {/* Trend */}
      <Card className="mt-6">
        <p className="font-semibold mb-3">Score trend over time</p>
        <TrendChart points={trend.data?.points ?? []} />
      </Card>

      {/* Two-column: radar + by type */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        <Card>
          <p className="font-semibold mb-3">Latest vs average — across dimensions</p>
          <RadarPanel latest={dims.data?.latest} average={dims.data?.average} />
        </Card>
        <Card>
          <p className="font-semibold mb-3">By interview type</p>
          <ByTypeBars items={byType.data?.items ?? []} />
        </Card>
      </section>

      {/* Top weaknesses */}
      <Card className="mt-6">
        <div className="flex items-center justify-between mb-3">
          <p className="font-semibold flex items-center gap-2">
            <AlertTriangle size={16} className="text-amber-500" />
            Top recurring weaknesses
          </p>
          {weak.data?.answers_analyzed != null && (
            <span className="text-xs text-slate-400">
              from {weak.data.answers_analyzed} answer{weak.data.answers_analyzed === 1 ? "" : "s"}
            </span>
          )}
        </div>
        {(weak.data?.top_weaknesses?.length ?? 0) === 0 ? (
          <p className="text-sm text-slate-500">
            No recurring weaknesses yet — keep going! 🎯
          </p>
        ) : (
          <ul className="space-y-2">
            {weak.data!.top_weaknesses.map((t: any) => (
              <li key={t.theme} className="flex items-center justify-between text-sm border-b border-slate-100 last:border-0 pb-2 last:pb-0">
                <span className="text-slate-700">{t.theme}</span>
                <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-xs font-medium">
                  ×{t.count}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {compareOpen && (
        <CompareDialog
          sessions={completedSessions as SessionLite[]}
          onClose={() => setCompareOpen(false)}
        />
      )}
    </div>
  );
}

function Stat({
  label, value, suffix, icon: Icon, tone = "default",
}: {
  label: string;
  value: string;
  suffix?: string;
  icon: any;
  tone?: "default" | "green" | "amber";
}) {
  const toneClass =
    tone === "green" ? "text-green-600"
    : tone === "amber" ? "text-amber-600"
    : "text-slate-900";
  return (
    <Card>
      <CardDescription>
        <Icon size={14} className="inline -mt-0.5 mr-1 text-slate-400" />
        {label}
      </CardDescription>
      <p className={`text-3xl font-bold tabular-nums ${toneClass}`}>
        {value}
        {value !== "—" && suffix && (
          <span className="text-sm font-normal text-slate-400">{suffix}</span>
        )}
      </p>
    </Card>
  );
}

function fmt(v: number | null | undefined) {
  return v == null ? "—" : v.toFixed(2);
}
