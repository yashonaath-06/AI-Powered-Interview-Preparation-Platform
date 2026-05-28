"use client";
/**
 * Live interview session — Phases 8 + 10.
 *
 * Voice-first answer flow (Whisper STT) and a live webcam panel that
 * uploads ~1 frame every 2 s for MediaPipe analysis. Per-question vision
 * summary is bundled with the answer submission so the scorer can fold it
 * into the engagement / confidence dimensions.
 */
import { useEffect, useMemo, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Volume2, ChevronRight, Flag, Pencil, Mic } from "lucide-react";
import toast from "react-hot-toast";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { RecordingControls } from "@/components/interview/RecordingControls";
import { WebcamPanel, WebcamPanelHandle } from "@/components/interview/WebcamPanel";
import { AudioRecorder } from "@/lib/audio";

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

type Mode = "voice" | "text";

export default function InterviewSessionPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const sessionId = Number(params.id);

  // Default to voice if browser supports it, otherwise text.
  const [mode, setMode] = useState<Mode>(() =>
    AudioRecorder.isSupported() ? "voice" : "text",
  );
  const [answer, setAnswer] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [lastTranscript, setLastTranscript] = useState<string | null>(null);
  const startedAt = useRef<number>(Date.now());
  const webcamRef = useRef<WebcamPanelHandle>(null);

  const progress = useQuery<Progress>({
    queryKey: ["interview-progress", sessionId],
    queryFn: async () =>
      (await api.get(`/api/interviews/${sessionId}`)).data,
    refetchOnWindowFocus: false,
  });

  // Reset state when a new question loads
  useEffect(() => {
    setAnswer("");
    setLastTranscript(null);
    startedAt.current = Date.now();
  }, [progress.data?.current_question?.id]);

  // Auto-redirect to report once session completes
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

  const handleAnswerSuccess = async (resp: any) => {
    const overall = resp?.scores?.overall;
    toast.success(`Scored: ${overall ?? "—"}/10`);
    if (resp?.transcript) setLastTranscript(resp.transcript);
    if (resp.finished) {
      await complete();
    } else {
      await progress.refetch();
    }
  };

  const submitText = async () => {
    if (!answer.trim()) {
      toast.error("Please type your answer first.");
      return;
    }
    setSubmitting(true);
    try {
      const duration = (Date.now() - startedAt.current) / 1000;
      const visionSummary = await webcamRef.current?.getSummaryAndReset();
      const { data } = await api.post(`/api/interviews/${sessionId}/answer`, {
        answer_text: answer,
        duration_seconds: duration,
        vision_summary: visionSummary,
      });
      await handleAnswerSuccess(data);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to submit answer");
    } finally {
      setSubmitting(false);
    }
  };

  const submitAudio = async (blob: Blob, ext: string) => {
    setSubmitting(true);
    try {
      const fd = new FormData();
      fd.append("audio", blob, `answer.${ext}`);
      const visionSummary = await webcamRef.current?.getSummaryAndReset();
      if (visionSummary) {
        fd.append("vision_summary", JSON.stringify(visionSummary));
      }
      const { data } = await api.post(
        `/api/interviews/${sessionId}/answer/audio`,
        fd,
        { headers: { "Content-Type": "multipart/form-data" } },
      );
      await handleAnswerSuccess(data);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || "Failed to upload answer";
      toast.error(detail);
      if (err?.response?.status === 503) setMode("text");
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
  const progressPct = useMemo(() => (total ? (answeredCount / total) * 100 : 0), [answeredCount, total]);

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

      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden mb-8">
        <div
          className="h-full bg-brand-500 transition-all duration-500"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* Live webcam panel */}
      {q && (
        <div className="mb-6">
          <WebcamPanel ref={webcamRef} sessionId={sessionId} />
        </div>
      )}

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

      {/* Mode toggle */}
      {q && AudioRecorder.isSupported() && (
        <div className="flex items-center gap-2 mt-6 mb-3 text-sm">
          <span className="text-slate-500 mr-2">Answer mode:</span>
          <button
            onClick={() => setMode("voice")}
            className={`px-3 py-1.5 rounded-lg border ${mode === "voice" ? "border-brand-500 bg-brand-50 text-brand-700" : "border-slate-200 text-slate-600 hover:border-slate-300"}`}
          >
            <Mic size={14} className="inline -mt-0.5 mr-1" /> Voice
          </button>
          <button
            onClick={() => setMode("text")}
            className={`px-3 py-1.5 rounded-lg border ${mode === "text" ? "border-brand-500 bg-brand-50 text-brand-700" : "border-slate-200 text-slate-600 hover:border-slate-300"}`}
          >
            <Pencil size={14} className="inline -mt-0.5 mr-1" /> Text
          </button>
          <span className="ml-auto text-xs text-slate-400">
            {isLast ? "Last question" : `${total - answeredCount - 1} more after this`}
          </span>
        </div>
      )}

      {/* Voice mode */}
      {q && mode === "voice" && (
        <div className="mt-3 space-y-3">
          <RecordingControls
            disabled={submitting || completing}
            onComplete={(blob, ext) => submitAudio(blob, ext)}
          />
          {lastTranscript && (
            <Card className="bg-slate-50 border-slate-200">
              <p className="text-xs uppercase tracking-widest text-slate-500 mb-1">
                Last transcript
              </p>
              <p className="text-sm text-slate-700">{lastTranscript}</p>
            </Card>
          )}
          <p className="text-xs text-slate-400">
            🛡️ Your audio is processed by an open-source Whisper model running on the
            backend; nothing is sent to third parties.
          </p>
        </div>
      )}

      {/* Text mode */}
      {q && mode === "text" && (
        <div className="mt-3">
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={7}
            placeholder="Type your answer. Aim for 50-180 words. Be specific and use concrete examples."
            className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-200"
          />
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-slate-400">
              {answer.trim().split(/\s+/).filter(Boolean).length} words
            </span>
            <Button onClick={submitText} loading={submitting} disabled={!answer.trim()}>
              {isLast ? "Submit & Finish" : "Submit & Next"} <ChevronRight size={16} />
            </Button>
          </div>
        </div>
      )}

      <p className="mt-8 text-xs text-slate-400 text-center">
        🤖 Powered by Whisper (speech) · sentence-transformers (NLP) · MediaPipe (vision)
      </p>
    </div>
  );
}
