"use client";
import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface Item {
  answer_id: number;
  question: string;
  category: string;
  transcript: string;
  scores: Record<string, any>;
  combined_score: number | null;
}

export function AnswerAccordion({ items }: { items: Item[] }) {
  const [open, setOpen] = useState<number | null>(items[0]?.answer_id ?? null);

  if (items.length === 0) {
    return <p className="p-6 text-slate-500 text-sm">No answers recorded.</p>;
  }

  return (
    <div className="divide-y divide-slate-100">
      {items.map((it, idx) => {
        const isOpen = open === it.answer_id;
        const score = it.combined_score ?? 0;
        const color =
          score >= 7.5 ? "text-green-600"
          : score >= 5 ? "text-brand-600"
          : score >= 3 ? "text-amber-600"
          : "text-red-600";

        return (
          <div key={it.answer_id}>
            <button
              onClick={() => setOpen(isOpen ? null : it.answer_id)}
              className="w-full flex items-center gap-3 p-4 text-left hover:bg-slate-50 transition"
            >
              <span className="w-7 h-7 rounded-full bg-slate-100 text-slate-600 text-xs font-semibold flex items-center justify-center shrink-0">
                {idx + 1}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{it.question}</p>
                <p className="text-xs text-slate-500 capitalize">{it.category}</p>
              </div>
              <span className={cn("text-sm font-semibold tabular-nums shrink-0", color)}>
                {score.toFixed(1)}/10
              </span>
              <ChevronDown
                size={16}
                className={cn("text-slate-400 transition-transform", isOpen && "rotate-180")}
              />
            </button>

            {isOpen && (
              <div className="px-4 pb-5 pl-14 space-y-3">
                <div>
                  <p className="text-xs uppercase text-slate-500 mb-1">Your answer</p>
                  <p className="text-sm text-slate-700 whitespace-pre-wrap">
                    {it.transcript || <em>(no transcript)</em>}
                  </p>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  {(["technical", "communication", "confidence", "engagement"] as const).map((k) => (
                    <div key={k} className="rounded-lg bg-slate-50 px-3 py-2">
                      <p className="text-slate-500 capitalize">{k}</p>
                      <p className="font-semibold text-slate-800 tabular-nums">
                        {(it.scores?.[k] ?? 0).toFixed(1)}
                      </p>
                    </div>
                  ))}
                </div>
                {Array.isArray(it.scores?.notes) && it.scores.notes.length > 0 && (
                  <ul className="text-xs text-amber-700 space-y-1 list-disc pl-5">
                    {it.scores.notes.map((n: string, i: number) => <li key={i}>{n}</li>)}
                  </ul>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
