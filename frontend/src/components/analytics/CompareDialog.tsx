"use client";
import { useState } from "react";
import toast from "react-hot-toast";
import { X } from "lucide-react";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export interface SessionLite {
  id: number;
  company: string | null;
  role: string | null;
  interview_type: string;
  started_at: string;
  overall_score: number | null;
}

interface ComparePayload {
  a: SessionDetail;
  b: SessionDetail;
}

interface SessionDetail {
  session_id: number;
  company: string | null;
  role: string | null;
  interview_type: string;
  started_at: string;
  ended_at: string | null;
  overall_score: number | null;
  scores: {
    technical: number | null;
    communication: number | null;
    confidence: number | null;
    engagement: number | null;
  };
  ai_feedback: string | null;
}

export function CompareDialog({
  sessions,
  onClose,
}: {
  sessions: SessionLite[];
  onClose: () => void;
}) {
  const [a, setA] = useState<number | "">(sessions[0]?.id ?? "");
  const [b, setB] = useState<number | "">(sessions[1]?.id ?? "");
  const [data, setData] = useState<ComparePayload | null>(null);
  const [loading, setLoading] = useState(false);

  const compare = async () => {
    if (!a || !b || a === b) {
      toast.error("Pick two different sessions.");
      return;
    }
    setLoading(true);
    try {
      const { data: resp } = await api.post("/api/analytics/compare", {
        session_a: a,
        session_b: b,
      });
      setData(resp);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Comparison failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto shadow-xl">
        <div className="flex items-center justify-between p-5 border-b border-slate-100">
          <h3 className="font-semibold">Compare two sessions</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700">
            <X size={18} />
          </button>
        </div>
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <SessionPicker label="Session A" value={a} onChange={setA} sessions={sessions} />
            <SessionPicker label="Session B" value={b} onChange={setB} sessions={sessions} />
          </div>
          <div className="text-right">
            <Button onClick={compare} loading={loading}>Compare</Button>
          </div>

          {data && (
            <div className="grid grid-cols-2 gap-4 mt-4">
              <SessionCard d={data.a} />
              <SessionCard d={data.b} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function SessionPicker({
  label,
  value,
  onChange,
  sessions,
}: {
  label: string;
  value: number | "";
  onChange: (v: number | "") => void;
  sessions: SessionLite[];
}) {
  return (
    <label className="block">
      <span className="block text-xs text-slate-500 mb-1.5">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value ? Number(e.target.value) : "")}
        className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200"
      >
        <option value="">— pick a session —</option>
        {sessions.map((s) => (
          <option key={s.id} value={s.id}>
            #{s.id} · {new Date(s.started_at).toLocaleDateString()} ·{" "}
            {s.company || "Generic"} · {s.interview_type} ·{" "}
            {s.overall_score != null ? `${s.overall_score}/10` : "—"}
          </option>
        ))}
      </select>
    </label>
  );
}

function SessionCard({ d }: { d: SessionDetail }) {
  return (
    <Card>
      <p className="text-xs uppercase text-slate-400 tracking-widest">
        Session #{d.session_id}
      </p>
      <p className="font-medium mt-1">
        {d.company || "Generic"} · {d.role || "any role"}
      </p>
      <p className="text-xs text-slate-500 capitalize">{d.interview_type}</p>

      <p className="text-3xl font-bold mt-3">
        {d.overall_score != null ? d.overall_score.toFixed(1) : "—"}
        <span className="text-sm font-normal text-slate-400"> / 10</span>
      </p>

      <ul className="mt-4 space-y-1.5 text-sm">
        {(["technical", "communication", "confidence", "engagement"] as const).map((k) => (
          <li key={k} className="flex justify-between">
            <span className="capitalize text-slate-600">{k}</span>
            <span className="font-medium tabular-nums">
              {d.scores?.[k] != null ? Number(d.scores[k]).toFixed(2) : "—"}
            </span>
          </li>
        ))}
      </ul>

      {d.ai_feedback && (
        <p className="mt-4 text-xs text-slate-500 line-clamp-3">{d.ai_feedback}</p>
      )}
    </Card>
  );
}
