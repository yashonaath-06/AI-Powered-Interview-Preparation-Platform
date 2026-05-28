"use client";
import { useEffect, useRef, useState } from "react";
import { Mic, Square, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

import { Button } from "@/components/ui/Button";
import { AudioRecorder } from "@/lib/audio";
import { cn } from "@/lib/utils";

interface Props {
  /** Called once the user stops recording — receives the encoded audio blob. */
  onComplete: (blob: Blob, extension: string) => Promise<void> | void;
  /** Block recording while a parent operation is in progress. */
  disabled?: boolean;
}

function fmtTime(seconds: number) {
  const m = Math.floor(seconds / 60).toString().padStart(2, "0");
  const s = Math.floor(seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export function RecordingControls({ onComplete, disabled }: Props) {
  const recorder = useRef<AudioRecorder | null>(null);
  const startTime = useRef<number>(0);
  const tickInterval = useRef<ReturnType<typeof setInterval> | null>(null);

  const [supported] = useState(() => AudioRecorder.isSupported());
  const [recording, setRecording] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [level, setLevel] = useState(0);

  useEffect(() => {
    return () => {
      if (tickInterval.current) clearInterval(tickInterval.current);
      recorder.current?.cancel();
    };
  }, []);

  if (!supported) {
    return (
      <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
        Your browser doesn&apos;t support audio recording. Please use the textarea below instead.
      </div>
    );
  }

  const start = async () => {
    try {
      recorder.current = new AudioRecorder();
      await recorder.current.start({ onLevel: setLevel });
      startTime.current = Date.now();
      setElapsed(0);
      setRecording(true);
      tickInterval.current = setInterval(() => {
        setElapsed((Date.now() - startTime.current) / 1000);
      }, 200);
    } catch (err: any) {
      console.error(err);
      toast.error(`Mic blocked. ${AudioRecorder.permissionsHint()}`);
    }
  };

  const stop = async () => {
    if (!recorder.current) return;
    setUploading(true);
    if (tickInterval.current) {
      clearInterval(tickInterval.current);
      tickInterval.current = null;
    }
    try {
      const blob = await recorder.current.stop();
      const ext = recorder.current.extensionGuess;
      setRecording(false);
      await onComplete(blob, ext);
    } catch (err: any) {
      console.error(err);
      toast.error("Could not finalize recording.");
    } finally {
      setUploading(false);
      recorder.current = null;
      setLevel(0);
      setElapsed(0);
    }
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 flex items-center gap-4">
      {/* Recording indicator */}
      <div className="relative w-14 h-14 flex items-center justify-center shrink-0">
        <span
          className={cn(
            "absolute inset-0 rounded-full transition",
            recording ? "bg-red-500/20" : "bg-slate-100",
          )}
          style={
            recording
              ? { transform: `scale(${1 + Math.min(level, 1) * 0.5})` }
              : undefined
          }
        />
        <div
          className={cn(
            "relative w-10 h-10 rounded-full flex items-center justify-center text-white",
            recording ? "bg-red-500" : "bg-brand-500",
          )}
        >
          {recording ? <Square size={16} fill="currentColor" /> : <Mic size={18} />}
        </div>
      </div>

      <div className="flex-1">
        <p className="text-sm font-medium">
          {recording ? "Recording..." : uploading ? "Transcribing..." : "Ready to record"}
        </p>
        <p className="text-xs text-slate-500">
          {recording
            ? `Speak naturally. Click Stop when you're done. (${fmtTime(elapsed)})`
            : "Click the mic, answer the question out loud, then stop. Whisper will transcribe."}
        </p>
      </div>

      {!recording ? (
        <Button onClick={start} disabled={disabled || uploading} variant="primary">
          {uploading ? <Loader2 size={16} className="animate-spin" /> : <Mic size={16} />}
          {uploading ? "Working…" : "Record"}
        </Button>
      ) : (
        <Button onClick={stop} variant="danger">
          <Square size={14} /> Stop ({fmtTime(elapsed)})
        </Button>
      )}
    </div>
  );
}
