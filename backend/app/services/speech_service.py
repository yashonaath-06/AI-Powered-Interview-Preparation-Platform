"""
Speech-to-Text via OpenAI Whisper (using the `faster-whisper` runtime).

Why faster-whisper?
  • 4× faster than openai-whisper on CPU
  • Same accuracy (uses CTranslate2)
  • Works fine without a GPU
  • PyAV-bundled ffmpeg → fewer system-level dependencies

Graceful fallback: if `faster-whisper` is not installed, the service is
"unavailable" and the audio endpoint returns 503 — the rest of the app
keeps working with text-typed answers.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from threading import Lock

from loguru import logger

from app.config import settings


try:
    from faster_whisper import WhisperModel  # type: ignore
    _AVAILABLE = True
except Exception:  # pragma: no cover
    WhisperModel = None  # type: ignore
    _AVAILABLE = False


_model = None
_model_lock = Lock()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_available() -> bool:
    """True iff faster-whisper was importable when the module was loaded."""
    return _AVAILABLE


@dataclass
class TranscriptionResult:
    transcript: str
    language: str | None
    duration_seconds: float | None
    word_count: int

    def to_dict(self) -> dict:
        return {
            "transcript": self.transcript,
            "language": self.language,
            "duration_seconds": self.duration_seconds,
            "word_count": self.word_count,
        }


def transcribe_bytes(
    audio_bytes: bytes,
    *,
    file_extension: str = "webm",
) -> TranscriptionResult:
    """
    Transcribe raw audio bytes (WebM, Ogg, Wav, MP4, MP3 — anything ffmpeg/PyAV
    can decode).

    Raises RuntimeError if the speech service isn't available.
    """
    if not _AVAILABLE:
        raise RuntimeError(
            "Whisper is not installed on this server. "
            "Install requirements-ml.txt to enable speech-to-text."
        )

    model = _get_model()

    suffix = f".{file_extension.lstrip('.')}"
    fd, path = tempfile.mkstemp(prefix="answer_", suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(audio_bytes)

        segments_iter, info = model.transcribe(
            path,
            beam_size=1,           # fastest: greedy decoding
            vad_filter=True,       # skip long silences
            language="en",         # MVP — assume English answers
            condition_on_previous_text=False,
        )

        segments = list(segments_iter)
        transcript = " ".join(s.text for s in segments).strip()
        word_count = len(transcript.split()) if transcript else 0

        return TranscriptionResult(
            transcript=transcript,
            language=getattr(info, "language", "en"),
            duration_seconds=float(getattr(info, "duration", 0.0)) or None,
            word_count=word_count,
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _get_model():
    """Lazy, thread-safe singleton load of the Whisper model."""
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model

        model_size = settings.whisper_model
        logger.info(f"Loading Whisper model {model_size!r} (one-time, may take a moment)...")
        _model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",  # great trade-off on CPU
        )
        logger.info("✅ Whisper model loaded.")
        return _model
