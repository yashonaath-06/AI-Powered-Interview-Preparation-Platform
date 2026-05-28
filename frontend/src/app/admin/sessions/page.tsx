"use client";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";

interface Item {
  session_id: number;
  user_id: number;
  user_email: string;
  user_name: string;
  company: string | null;
  role: string | null;
  interview_type: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  overall_score: number | null;
}

export default function AdminSessionsPage() {
  const data = useQuery<{ items: Item[] }>({
    queryKey: ["admin-sessions"],
    queryFn: async () => (await api.get("/api/admin/sessions", { params: { limit: 100 } })).data,
  });

  return (
    <div className="p-6 lg:p-10 max-w-6xl mx-auto">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Recent activity</h1>
        <p className="text-slate-500 text-sm mt-1">Last 100 interview sessions across all users.</p>
      </header>

      <Card className="p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="p-3">User</th>
              <th className="p-3">Target</th>
              <th className="p-3">Type</th>
              <th className="p-3">Status</th>
              <th className="p-3">Started</th>
              <th className="p-3 text-right">Score</th>
            </tr>
          </thead>
          <tbody>
            {data.isLoading ? (
              <tr><td className="p-6 text-center text-slate-400" colSpan={6}>Loading…</td></tr>
            ) : (data.data?.items.length ?? 0) === 0 ? (
              <tr><td className="p-6 text-center text-slate-400" colSpan={6}>No sessions yet.</td></tr>
            ) : data.data!.items.map((s) => (
              <tr key={s.session_id} className="border-t border-slate-100">
                <td className="p-3">
                  <p className="font-medium">{s.user_name}</p>
                  <p className="text-xs text-slate-500">{s.user_email}</p>
                </td>
                <td className="p-3">
                  {s.company || "Generic"}{s.role ? ` · ${s.role}` : ""}
                </td>
                <td className="p-3 capitalize">{s.interview_type}</td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    s.status === "completed"
                      ? "bg-green-50 text-green-700"
                      : s.status === "in_progress"
                      ? "bg-amber-50 text-amber-700"
                      : "bg-slate-100 text-slate-600"
                  }`}>
                    {s.status.replace("_", " ")}
                  </span>
                </td>
                <td className="p-3 text-slate-500">
                  {new Date(s.started_at).toLocaleString()}
                </td>
                <td className="p-3 text-right font-medium tabular-nums">
                  {s.overall_score != null ? `${s.overall_score}/10` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
