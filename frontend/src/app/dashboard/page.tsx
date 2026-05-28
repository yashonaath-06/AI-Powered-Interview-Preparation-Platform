"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { PlayCircle, Sparkles, TrendingUp } from "lucide-react";

import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface Summary {
  total_sessions: number;
  completed_sessions: number;
  average_score: number | null;
}

interface Session {
  id: number;
  company: string | null;
  role: string | null;
  interview_type: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  overall_score: number | null;
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  const summary = useQuery<Summary>({
    queryKey: ["analytics-summary"],
    queryFn: async () => (await api.get("/api/analytics/summary")).data,
  });

  const sessions = useQuery<Session[]>({
    queryKey: ["my-sessions"],
    queryFn: async () => (await api.get("/api/interviews")).data,
  });

  return (
    <div className="p-6 lg:p-10 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-2xl font-bold">
          Welcome back, {user?.full_name.split(" ")[0] || "there"} 👋
        </h1>
        <p className="text-slate-500 mt-1">
          Here&apos;s a snapshot of your interview prep journey.
        </p>
      </header>

      {/* Stat cards */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardDescription>Total sessions</CardDescription>
            <CardTitle className="text-3xl">
              {summary.data?.total_sessions ?? "—"}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Completed</CardDescription>
            <CardTitle className="text-3xl">
              {summary.data?.completed_sessions ?? "—"}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Average score</CardDescription>
            <CardTitle className="text-3xl">
              {summary.data?.average_score != null
                ? `${summary.data.average_score}/10`
                : "—"}
            </CardTitle>
          </CardHeader>
        </Card>
      </section>

      {/* CTA card */}
      <Card className="mt-8 bg-gradient-to-br from-brand-500 to-purple-600 text-white border-0">
        <CardHeader className="mb-0">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <CardTitle className="text-white text-xl">
                Ready for your next mock interview?
              </CardTitle>
              <p className="text-white/80 text-sm mt-1">
                Pick a company &amp; role and let our AI take over.
              </p>
            </div>
            <Link href="/dashboard/interview">
              <Button variant="secondary" size="lg" className="bg-white text-slate-900 hover:bg-slate-100">
                <PlayCircle size={18} /> Start interview
              </Button>
            </Link>
          </div>
        </CardHeader>
      </Card>

      {/* Recent sessions */}
      <section className="mt-10">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp size={18} /> Recent sessions
        </h2>

        {sessions.isLoading ? (
          <p className="text-slate-500 text-sm">Loading…</p>
        ) : sessions.data && sessions.data.length > 0 ? (
          <Card className="p-0 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
                <tr>
                  <th className="p-3">Date</th>
                  <th className="p-3">Company / Role</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Score</th>
                </tr>
              </thead>
              <tbody>
                {sessions.data.map((s) => (
                  <tr key={s.id} className="border-t border-slate-100">
                    <td className="p-3">
                      {new Date(s.started_at).toLocaleDateString()}
                    </td>
                    <td className="p-3">
                      {s.company ?? "—"} {s.role ? `· ${s.role}` : ""}
                    </td>
                    <td className="p-3 capitalize">{s.interview_type}</td>
                    <td className="p-3 capitalize">{s.status.replace("_", " ")}</td>
                    <td className="p-3 text-right font-medium">
                      {s.overall_score != null ? `${s.overall_score}/10` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        ) : (
          <Card className="text-center py-12">
            <Sparkles size={28} className="mx-auto text-slate-300 mb-3" />
            <p className="font-medium">No sessions yet</p>
            <p className="text-sm text-slate-500 mt-1">
              Your interview history will appear here.
            </p>
          </Card>
        )}
      </section>
    </div>
  );
}
