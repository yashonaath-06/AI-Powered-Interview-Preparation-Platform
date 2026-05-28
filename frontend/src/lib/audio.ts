/**
 * Tiny wrapper around the browser MediaRecorder API.
 *
 *   const r = new AudioRecorder();
 *   await r.start();          // asks for mic permission
 *   ...user speaks...
 *   const blob = await r.stop();
 *
 * The blob is whatever MIME the browser emits (Chrome/Edge: audio/webm,
 * Firefox: audio/ogg, Safari: audio/mp4). The backend hands it directly to
 * ffmpeg/PyAV which understands all of them.
 */

export interface RecorderOptions {
  /** Called every 100 ms with the latest peak amplitude (0–1) for waveforms. */
  onLevel?: (level: number) => void;
}

export class AudioRecorder {
  private stream: MediaStream | null = null;
  private rec: MediaRecorder | null = null;
  private chunks: Blob[] = [];
  private analyserCleanup?: () => void;

  private mimeType: string = "audio/webm";

  static isSupported() {
    return (
      typeof window !== "undefined" &&
      "mediaDevices" in navigator &&
      typeof window.MediaRecorder !== "undefined"
    );
  }

  static permissionsHint(): string {
    return (
      "Click the lock icon in your browser's address bar and allow " +
      "microphone access for this site, then refresh."
    );
  }

  async start(opts: RecorderOptions = {}): Promise<void> {
    if (!AudioRecorder.isSupported()) {
      throw new Error("MediaRecorder is not supported in this browser.");
    }

    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });

    // Pick the best supported MIME type
    const candidates = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/mp4",
    ];
    this.mimeType =
      candidates.find((t) => window.MediaRecorder.isTypeSupported(t)) || "audio/webm";

    this.rec = new MediaRecorder(this.stream, { mimeType: this.mimeType });
    this.chunks = [];
    this.rec.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) this.chunks.push(e.data);
    };
    this.rec.start(250); // emit a chunk every 250ms

    if (opts.onLevel) {
      this.startLevelMonitor(opts.onLevel);
    }
  }

  /** Returns the recorded blob and frees the mic. */
  async stop(): Promise<Blob> {
    if (!this.rec) throw new Error("Recorder is not started.");

    const blob = await new Promise<Blob>((resolve) => {
      this.rec!.onstop = () => {
        const out = new Blob(this.chunks, { type: this.mimeType });
        resolve(out);
      };
      this.rec!.stop();
    });

    this.cleanup();
    return blob;
  }

  cancel(): void {
    if (this.rec && this.rec.state !== "inactive") {
      this.rec.stop();
    }
    this.cleanup();
  }

  get extensionGuess(): string {
    if (this.mimeType.startsWith("audio/webm")) return "webm";
    if (this.mimeType.startsWith("audio/ogg")) return "ogg";
    if (this.mimeType.startsWith("audio/mp4")) return "m4a";
    return "webm";
  }

  // ---- private --------------------------------------------------------

  private cleanup() {
    this.analyserCleanup?.();
    this.analyserCleanup = undefined;
    this.stream?.getTracks().forEach((t) => t.stop());
    this.stream = null;
    this.rec = null;
  }

  private startLevelMonitor(onLevel: (l: number) => void) {
    if (!this.stream) return;
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const src = ctx.createMediaStreamSource(this.stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 512;
    src.connect(analyser);
    const buf = new Uint8Array(analyser.frequencyBinCount);

    let raf = 0;
    const tick = () => {
      analyser.getByteTimeDomainData(buf);
      // Normalise to 0..1 amplitude
      let peak = 0;
      for (let i = 0; i < buf.length; i++) {
        const v = Math.abs(buf[i] - 128) / 128;
        if (v > peak) peak = v;
      }
      onLevel(peak);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    this.analyserCleanup = () => {
      cancelAnimationFrame(raf);
      ctx.close().catch(() => {});
    };
  }
}
