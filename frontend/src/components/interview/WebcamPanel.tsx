"use client";
import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import { CameraOff, Eye, Smile, User } from "lucide-react";

import { api } from "@/lib/api";
import { Webcam } from "@/lib/webcam";
import { cn } from "@/lib/utils";

export interface FrameMetrics {
  face_detected: boolean;
  face_count: number;
  head_yaw_deg: number | null;
  head_pitch_deg: number | null;
  head_roll_deg: number | null;
  gaze_x: number | null;
  gaze_y: number | null;
  eye_contact: boolean | null;
  smile_score: number | null;
  notes: string[];
}

export interface WebcamPanelHandle {
  /** Returns aggregated metrics + clears the buffer for the next question. */
  getSummaryAndReset: () => Promise<any | null>;
  isActive: () => boolean;
}

interface Props {
  sessionId: number;
  /** Capture interval in ms. Default 2000 (one frame every 2 seconds). */
  intervalMs?: number;
  enabled?: boolean;
}

export const WebcamPanel = forwardRef<WebcamPanelHandle, Props>(function WebcamPanel(
  { sessionId, intervalMs = 2000, enabled = true },
  ref,
) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const camRef = useRef<Webcam | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const framesRef = useRef<FrameMetrics[]>([]);

  const [active, setActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latest, setLatest] = useState<FrameMetrics | null>(null);
  const [unsupported] = useState(() => !Webcam.isSupported());

  useImperativeHandle(ref, () => ({
    isActive: () => active,
    getSummaryAndReset: async () => {
      if (framesRef.current.length === 0) return null;
      try {
        const { data } = await api.post(
          `/api/interviews/${sessionId}/vision/aggregate`,
          framesRef.current,
        );
        framesRef.current = [];
        return data;
      } catch {
        framesRef.current = [];
        return null;
      }
    },
  }));

  useEffect(() => {
    if (!enabled || unsupported) return;

    let cancelled = false;
    (async () => {
      try {
        if (!videoRef.current) return;
        camRef.current = new Webcam(videoRef.current);
        await camRef.current.start();
        if (cancelled) {
          camRef.current.stop();
          return;
        }
        setActive(true);
        intervalRef.current = setInterval(captureAndAnalyze, intervalMs);
      } catch (err: any) {
        setError(err?.message || "Could not access camera");
      }
    })();

    return () => {
      cancelled = true;
      if (intervalRef.current) clearInterval(intervalRef.current);
      camRef.current?.stop();
      setActive(false);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, sessionId]);

  const captureAndAnalyze = async () => {
    try {
      if (!camRef.current) return;
      const blob = await camRef.current.captureFrame();
      const fd = new FormData();
      fd.append("image", blob, "frame.jpg");
      const { data } = await api.post(
        `/api/interviews/${sessionId}/vision/frame`,
        fd,
        { headers: { "Content-Type": "multipart/form-data" } },
      );
      framesRef.current.push(data);
      setLatest(data);
    } catch (err: any) {
      // 503 = vision not enabled on the server. Stop trying.
      if (err?.response?.status === 503) {
        setError("Server CV not enabled");
        if (intervalRef.current) clearInterval(intervalRef.current);
      }
    }
  };

  if (unsupported) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
        <CameraOff size={14} className="inline -mt-0.5 mr-1" />
        Your browser doesn&apos;t support webcam capture.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3">
      <div className="flex gap-3 items-start">
        <div className="relative w-44 aspect-[4/3] bg-slate-900 rounded-lg overflow-hidden shrink-0">
          {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
          <video ref={videoRef} className="w-full h-full object-cover -scale-x-100" />
          {!active && !error && (
            <div className="absolute inset-0 flex items-center justify-center text-white/70 text-xs">
              starting…
            </div>
          )}
          {active && (
            <span className="absolute top-2 left-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-500 text-white text-[10px]">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" /> LIVE
            </span>
          )}
        </div>

        <div className="flex-1 min-w-0">
          {error ? (
            <p className="text-xs text-amber-700">{error}</p>
          ) : (
            <>
              <p className="text-xs uppercase tracking-widest text-slate-400 mb-1">
                Live signals
              </p>
              <div className="grid grid-cols-2 gap-1.5 text-xs">
                <SignalRow
                  icon={User}
                  label="Face"
                  value={latest ? (latest.face_detected ? "Detected" : "Missing") : "—"}
                  good={latest?.face_detected ?? null}
                />
                <SignalRow
                  icon={Eye}
                  label="Eye contact"
                  value={
                    latest?.eye_contact === true ? "Yes"
                    : latest?.eye_contact === false ? "Off"
                    : "—"
                  }
                  good={latest?.eye_contact ?? null}
                />
                <SignalRow
                  label="Head yaw"
                  value={
                    latest?.head_yaw_deg != null
                      ? `${latest.head_yaw_deg.toFixed(0)}°`
                      : "—"
                  }
                />
                <SignalRow
                  icon={Smile}
                  label="Smile"
                  value={
                    latest?.smile_score != null
                      ? `${Math.round(latest.smile_score * 100)}%`
                      : "—"
                  }
                />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
});

function SignalRow({
  icon: Icon,
  label,
  value,
  good,
}: {
  icon?: any;
  label: string;
  value: string;
  good?: boolean | null;
}) {
  const tone =
    good === true ? "text-green-600"
    : good === false ? "text-amber-600"
    : "text-slate-700";
  return (
    <div className="flex items-center gap-1.5">
      {Icon && <Icon size={12} className="text-slate-400 shrink-0" />}
      <span className="text-slate-500">{label}:</span>
      <span className={cn("font-medium tabular-nums", tone)}>{value}</span>
    </div>
  );
}
