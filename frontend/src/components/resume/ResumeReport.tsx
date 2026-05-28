"use client";
import { Card } from "@/components/ui/Card";
import { ScoreRing } from "@/components/interview/ScoreRing";
import { CheckCircle2, XCircle } from "lucide-react";

export interface ResumeAnalysis {
  id: number;
  filename: string;
  target_role: string | null;
  match_score: number;
  ai_feedback: string;
  raw_text_preview: string;
  parsed_skills: string[];
  matched_skills: string[];
  missing_skills: string[];
  skill_categories: Record<string, string[]>;
  detected_sections: string[];
  word_count: number | null;
  semantic_score: number | null;
  notes: string[];
  created_at: string;
}

export function ResumeReport({ analysis }: { analysis: ResumeAnalysis }) {
  return (
    <>
      {/* Score + summary */}
      <div className="grid grid-cols-1 md:grid-cols-[260px_1fr] gap-6">
        <Card className="flex flex-col items-center justify-center py-8">
          <ScoreRing value={analysis.match_score / 10} max={10} />
          <p className="mt-4 text-sm text-slate-500">Match score</p>
          <p className="text-xs text-slate-400">
            {analysis.match_score.toFixed(1)} / 100
          </p>
        </Card>

        <Card>
          <p className="font-semibold mb-3">Quick stats</p>
          <ul className="space-y-2 text-sm">
            <Row k="Target role"        v={analysis.target_role || "Generic"} />
            <Row k="Skills detected"    v={String(analysis.parsed_skills.length)} />
            <Row k="Matched"            v={String(analysis.matched_skills.length)} tone="green" />
            <Row k="Missing"            v={String(analysis.missing_skills.length)} tone="amber" />
            <Row k="Word count"         v={String(analysis.word_count ?? "—")} />
            <Row k="Sections detected"  v={analysis.detected_sections.join(", ") || "—"} />
            {analysis.semantic_score != null && (
              <Row k="Semantic similarity" v={`${(analysis.semantic_score * 100).toFixed(0)}%`} />
            )}
          </ul>
        </Card>
      </div>

      {/* Skills */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <Card>
          <p className="font-semibold mb-3 flex items-center gap-2">
            <CheckCircle2 size={16} className="text-green-600" />
            Matched skills ({analysis.matched_skills.length})
          </p>
          {analysis.matched_skills.length === 0 ? (
            <p className="text-sm text-slate-500">None matched the target role yet.</p>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {analysis.matched_skills.map((s) => (
                <span key={s} className="px-2 py-1 rounded-md bg-green-50 text-green-700 text-xs font-medium">
                  {s}
                </span>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <p className="font-semibold mb-3 flex items-center gap-2">
            <XCircle size={16} className="text-amber-500" />
            Missing skills ({analysis.missing_skills.length})
          </p>
          {analysis.missing_skills.length === 0 ? (
            <p className="text-sm text-slate-500">No major gaps for this role 🎯</p>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {analysis.missing_skills.map((s) => (
                <span key={s} className="px-2 py-1 rounded-md bg-amber-50 text-amber-700 text-xs font-medium">
                  {s}
                </span>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* All skills by category */}
      {Object.keys(analysis.skill_categories || {}).length > 0 && (
        <Card className="mt-4">
          <p className="font-semibold mb-3">All skills by category</p>
          <div className="space-y-3">
            {Object.entries(analysis.skill_categories).map(([cat, items]) => (
              <div key={cat}>
                <p className="text-xs uppercase tracking-widest text-slate-400 mb-1">{cat}</p>
                <div className="flex flex-wrap gap-1.5">
                  {items.map((s) => (
                    <span key={s} className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-xs">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Notes */}
      {analysis.notes.length > 0 && (
        <Card className="mt-4">
          <p className="font-semibold mb-3">Quick notes</p>
          <ul className="space-y-1.5 text-sm text-amber-700 list-disc pl-5">
            {analysis.notes.map((n, i) => (<li key={i}>{n}</li>))}
          </ul>
        </Card>
      )}

      {/* AI feedback */}
      <Card className="mt-4">
        <p className="font-semibold mb-3">AI Coach Feedback</p>
        <div className="prose prose-sm max-w-none text-slate-700 whitespace-pre-wrap">
          {analysis.ai_feedback}
        </div>
      </Card>
    </>
  );
}

function Row({
  k, v, tone,
}: { k: string; v: string; tone?: "green" | "amber" }) {
  const c =
    tone === "green" ? "text-green-700"
    : tone === "amber" ? "text-amber-700"
    : "text-slate-900";
  return (
    <li className="flex justify-between border-b border-slate-100 last:border-0 pb-2 last:pb-0">
      <span className="text-slate-500">{k}</span>
      <span className={`font-medium ${c}`}>{v}</span>
    </li>
  );
}
