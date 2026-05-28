"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, RotateCcw } from "lucide-react";

import { api } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ScoreRing } from "@/components/interview/ScoreRing";
import { ScoreBars } from "@/components/interview/ScoreBars";
import { AnswerAccordion } from "@/components/interview/AnswerAccordion";

interface Report {
  session: {
    id: number;
    company: string | null;
    role: string | null;
    interview_type: string;
    started_at: string;
    overall_score: number | null;
  };
  summary: {
    technical: number;
    communication: number;
    confidence: number;
    engagement: number;
    overall: number;
    answers_scored: number;
  } | null;
  ai_feedback: string | null;
  items: Array<{
    answer_id: number;
    question: string;
    category: string;
    transcript: string;
    scores: Record<string, any>;
    combined_score: number | null;
  }>;
}

export default function ReportPage() {
  const params = useParams<{ id: string }>();
  const sessionId = Number(params.id);

  const report = useQuery<Report>({
    queryKey: ["interview-report", sessionId],
    queryFn: async () => (await api.get(`/api/interviews/${sessionId}/report`)).data,
  });

  if (report.isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-slate-500">
        Loading report…
      </div>
    );
  }
  if (!report.data || !report.data.summary) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-slate-500">
        Report not available yet.
      </div>
    );
  }

  const { session, summary, ai_feedback, items } = report.data;

  return (
    <div className="p-6 lg:p-10 max-w-5xl mx-auto">
      <header className="flex items-center justify-between mb-6">
        <div>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800"
          >
            <ArrowLeft size={14} /> Back to dashboard
          </Link>
          <h1 className="text-2xl font-bold mt-1">Interview Report</h1>
          <p className="text-slate-500 text-sm mt-1">
            {session.company || "Generic"} · {session.role || "any role"} ·{" "}
            <span className="capitalize">{session.interview_type}</span>
          </p>
        </div>
        <Link href="/dashboard/interview">
          <Button variant="outline" size="sm">
            <RotateCcw size={14} /> Take another
          </Button>
        </Link>
      </header>

      {/* Top: ring + bars */}
      <div className="grid grid-cols-1 md:grid-cols-[260px_1fr] gap-6">
        <Card className="flex flex-col items-center justify-center py-8">
          <ScoreRing value={summary.overall} max={10} />
          <p className="mt-4 text-sm text-slate-500">Overall score</p>
        </Card>
        <Card>
          <p className="font-semibold mb-4">Score breakdown</p>
          <ScoreBars summary={summary} />
        </Card>
      </div>

      {/* AI feedback */}
      {ai_feedback && (
        <Card className="mt-6">
          <p className="font-semibold mb-3">AI Coach Feedback</p>
          <div className="prose prose-sm max-w-none text-slate-700 whitespace-pre-wrap">
            {ai_feedback}
          </div>
        </Card>
      )}

      {/* Per-question */}
      <Card className="mt-6 p-0 overflow-hidden">
        <div className="p-6 border-b border-slate-100">
          <p className="font-semibold">Per-question breakdown</p>
        </div>
        <AnswerAccordion items={items} />
      </Card>
    </div>
  );
}
