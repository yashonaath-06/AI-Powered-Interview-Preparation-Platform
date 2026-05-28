/**
 * Webcam helper — getUserMedia + frame capture as JPEG Blob.
 *
 *   const cam = new Webcam(videoElement);
 *   await cam.start();         // user grants camera permission
 *   const blob = await cam.captureFrame();  // returns image/jpeg Blob
 *   cam.stop();
 */
export class Webcam {
  private stream: MediaStream | null = null;
  private canvas: HTMLCanvasElement | null = null;

  constructor(private video: HTMLVideoElement) {}

  static isSupported(): boolean {
    return typeof window !== "undefined" && !!navigator.mediaDevices?.getUserMedia;
  }

  static permissionsHint(): string {
    return (
      "Click the lock icon next to the URL and allow camera access for this site, then refresh."
    );
  }

  async start(): Promise<void> {
    this.stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
      audio: false,
    });
    this.video.srcObject = this.stream;
    this.video.muted = true;
    this.video.playsInline = true;
    await this.video.play();
  }

  /** Capture a downscaled JPEG of the current frame. */
  async captureFrame(maxWidth = 320, quality = 0.7): Promise<Blob> {
    if (!this.video.videoWidth) {
      throw new Error("Video not ready");
    }
    if (!this.canvas) this.canvas = document.createElement("canvas");
    const ratio = this.video.videoHeight / this.video.videoWidth;
    const w = Math.min(maxWidth, this.video.videoWidth);
    const h = Math.round(w * ratio);
    this.canvas.width = w;
    this.canvas.height = h;
    const ctx = this.canvas.getContext("2d");
    if (!ctx) throw new Error("No canvas context");
    ctx.drawImage(this.video, 0, 0, w, h);

    return await new Promise<Blob>((resolve, reject) => {
      this.canvas!.toBlob(
        (b) => (b ? resolve(b) : reject(new Error("toBlob failed"))),
        "image/jpeg",
        quality,
      );
    });
  }

  stop(): void {
    this.stream?.getTracks().forEach((t) => t.stop());
    this.stream = null;
    if (this.video.srcObject) this.video.srcObject = null;
  }
}
