"use client";
import { useQuery } from "@tanstack/react-query";
import { Users, Briefcase, Activity, Award } from "lucide-react";
import { Card, CardDescription } from "@/components/ui/Card";
import { api } from "@/lib/api";

interface Stats {
  user_count: number;
  admin_count: number;
  question_count: number;
  session_count: number;
  completed_session_count: number;
  completion_rate_pct: number;
  answer_count: number;
  platform_average_score: number | null;
  top_companies: { company: string; count: number }[];
  newest_users: {
    id: number;
    email: string;
    full_name: string;
    role: string;
    created_at: string;
  }[];
}

export default function AdminOverviewPage() {
  const stats = useQuery<Stats>({
    queryKey: ["admin-stats"],
    queryFn: async () => (await api.get("/api/admin/stats")).data,
  });

  return (
    <div className="p-6 lg:p-10 max-w-6xl mx-auto">
      <header className="mb-8">
        <h1 className="text-2xl font-bold">Admin overview</h1>
        <p className="text-slate-500 text-sm mt-1">
          Platform-wide metrics and recent activity.
        </p>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat label="Users"        icon={Users}     value={stats.data?.user_count ?? "—"}
              hint={stats.data ? `${stats.data.admin_count} admin${stats.data.admin_count === 1 ? "" : "s"}` : undefined} />
        <Stat label="Questions"    icon={Briefcase} value={stats.data?.question_count ?? "—"} />
        <Stat label="Sessions"     icon={Activity}  value={stats.data?.session_count ?? "—"}
              hint={stats.data ? `${stats.data.completion_rate_pct}% completed` : undefined} />
        <Stat label="Avg score"    icon={Award}
              value={stats.data?.platform_average_score != null ? `${stats.data.platform_average_score}/10` : "—"}
              hint={stats.data ? `over ${stats.data.answer_count} answers` : undefined} />
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        <Card>
          <p className="font-semibold mb-3">Top target companies</p>
          {(stats.data?.top_companies?.length ?? 0) === 0 ? (
            <p className="text-sm text-slate-500">No company data yet.</p>
          ) : (
            <ul className="space-y-2">
              {stats.data!.top_companies.map((c) => (
                <li key={c.company} className="flex items-center justify-between text-sm border-b border-slate-100 last:border-0 pb-2 last:pb-0">
                  <span className="text-slate-700">{c.company}</span>
                  <span className="px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 text-xs font-medium">
                    {c.count} session{c.count === 1 ? "" : "s"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card>
          <p className="font-semibold mb-3">Newest users</p>
          {(stats.data?.newest_users?.length ?? 0) === 0 ? (
            <p className="text-sm text-slate-500">No users yet.</p>
          ) : (
            <ul className="space-y-2">
              {stats.data!.newest_users.map((u) => (
                <li key={u.id} className="flex items-center justify-between text-sm border-b border-slate-100 last:border-0 pb-2 last:pb-0">
                  <div className="min-w-0">
                    <p className="font-medium truncate">{u.full_name}</p>
                    <p className="text-xs text-slate-500 truncate">{u.email}</p>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.role === "admin" ? "bg-amber-50 text-amber-700" : "bg-slate-100 text-slate-600"}`}>
                    {u.role}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </section>
    </div>
  );
}

function Stat({ label, icon: Icon, value, hint }: { label: string; icon: any; value: any; hint?: string }) {
  return (
    <Card>
      <CardDescription>
        <Icon size={14} className="inline -mt-0.5 mr-1 text-slate-400" /> {label}
      </CardDescription>
      <p className="text-3xl font-bold tabular-nums">{value}</p>
      {hint && <p className="text-xs text-slate-400 mt-1">{hint}</p>}
    </Card>
  );
}
