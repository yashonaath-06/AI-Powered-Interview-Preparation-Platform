"use client";
/**
 * Live interview session — Phase 7 baseline.
 *
 * Webcam capture and real audio recording are wired up in Phases 8-10.
 * For now the candidate types their answer; the engine still scores it
 * with the baseline scorer (which Phase 9 will replace).
 */
import { useEffect, useMemo, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Volume2, ChevronRight, Flag } from "lucide-react";
import toast from "react-hot-toast";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

interface Question {
  id: number;
  text: string;
  category: string;
  difficulty: string;
}

interface Progress {
  session: {
    id: number;
    company: string | null;
    role: string | null;
    interview_type: string;
    status: string;
  };
  answered_count: number;
  total_questions: number;
  current_question: Question | null;
}

export default function InterviewSessionPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const sessionId = Number(params.id);

  const [answer, setAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [completing, setCompleting] = useState(false);
  const startedAt = useRef<number>(Date.now());

  const progress = useQuery<Progress>({
    queryKey: ["interview-progress", sessionId],
    queryFn: async () =>
      (await api.get(`/api/interviews/${sessionId}`)).data,
    refetchOnWindowFocus: false,
  });

  // Reset timer + clear textarea when a new question loads
  useEffect(() => {
    setAnswer("");
    startedAt.current = Date.now();
  }, [progress.data?.current_question?.id]);

  // Auto-redirect to report once the session is complete
  useEffect(() => {
    if (progress.data?.session.status === "completed") {
      router.replace(`/dashboard/interview/${sessionId}/report`);
    }
  }, [progress.data?.session.status, router, sessionId]);

  const speak = () => {
    const q = progress.data?.current_question;
    if (!q || typeof window === "undefined" || !window.speechSynthesis) return;
    const u = new SpeechSynthesisUtterance(q.text);
    u.rate = 0.95;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  };

  const submit = async () => {
    if (!answer.trim()) {
      toast.error("Please type your answer first.");
      return;
    }
    setSubmitting(true);
    try {
      const duration = (Date.now() - startedAt.current) / 1000;
      const { data } = await api.post(`/api/interviews/${sessionId}/answer`, {
        answer_text: answer,
        duration_seconds: duration,
      });
      // Show the score for the just-submitted answer
      const overall = data.scores?.overall;
      toast.success(`Answer scored: ${overall ?? "—"}/10`);
      if (data.finished) {
        await complete();
      } else {
        await progress.refetch();
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to submit answer");
    } finally {
      setSubmitting(false);
    }
  };

  const complete = async () => {
    setCompleting(true);
    try {
      await api.post(`/api/interviews/${sessionId}/complete`);
      router.replace(`/dashboard/interview/${sessionId}/report`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Could not complete session");
    } finally {
      setCompleting(false);
    }
  };

  const data = progress.data;
  const q = data?.current_question;
  const answeredCount = data?.answered_count ?? 0;
  const total = data?.total_questions ?? 0;
  const isLast = answeredCount + 1 >= total;
  const progressPct = useMemo(() => {
    if (!total) return 0;
    return Math.round((answeredCount / total) * 100);
  }, [answeredCount, total]);

  if (progress.isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-slate-500">
        Loading session…
      </div>
    );
  }

  if (progress.isError || !data) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center text-slate-500">
        Could not load this session.
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-10 max-w-3xl mx-auto">
      {/* Top bar */}
      <header className="flex items-center justify-between mb-6">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">
            {data.session.company || "Generic"} · {data.session.role || "any role"} · {data.session.interview_type}
          </p>
          <p className="text-sm text-slate-600 mt-1">
            Question <strong>{Math.min(answeredCount + 1, total)}</strong> of{" "}
            <strong>{total}</strong>
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={complete}
          loading={completing}
          disabled={submitting || completing}
        >
          <Flag size={14} /> End early
        </Button>
      </header>

      {/* Progress bar */}
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden mb-8">
        <div
          className="h-full bg-brand-500 transition-all duration-500"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* Question card */}
      {q ? (
        <Card className="text-center py-12">
          <p className="text-xs uppercase tracking-widest text-brand-600 font-semibold mb-3">
            {q.category} · {q.difficulty}
          </p>
          <p className="text-xl md:text-2xl font-medium leading-relaxed">{q.text}</p>
          <button
            onClick={speak}
            className="mt-6 text-sm text-slate-500 hover:text-slate-800 inline-flex items-center gap-1.5"
          >
            <Volume2 size={16} /> Read it aloud
          </button>
        </Card>
      ) : (
        <Card className="text-center py-12 text-slate-500">
          No active question. <Button onClick={complete} loading={completing}>Finish</Button>
        </Card>
      )}

      {/* Answer textarea */}
      {q && (
        <div className="mt-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Your answer
          </label>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={7}
            placeholder="Speak the answer in your head and type it here. Aim for 50-180 words. Be specific and use concrete examples."
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200"
          />
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-slate-400">
              {answer.trim().split(/\s+/).filter(Boolean).length} words
            </span>
            <Button onClick={submit} loading={submitting} disabled={!answer.trim()}>
              {isLast ? "Submit & Finish" : "Submit & Next"} <ChevronRight size={16} />
            </Button>
          </div>
        </div>
      )}

      <p className="mt-8 text-xs text-slate-400 text-center">
        🎙️ Voice answers and 📷 webcam analysis will be enabled in Phase 8 &amp; 10.
      </p>
    </div>
  );
}
