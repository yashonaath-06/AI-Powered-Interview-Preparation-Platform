"""
Computer-vision analysis of interview webcam frames.

Pipeline (per frame, ~50ms on CPU)
----------------------------------
    JPEG bytes  ──►  PIL → numpy → BGR
                       │
                       ▼
              MediaPipe FaceMesh (468 + 10 iris landmarks)
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   face presence   head pose      gaze direction
                  (cv2.solvePnP)  (iris vs eye corners)
        │
        ▼
        smile / mouth-curve heuristic
        │
        ▼
    FrameMetrics (face_detected, head_yaw_deg, head_pitch_deg,
                  gaze_x, gaze_y, eye_contact, smile_score, ...)

Aggregation
-----------
The frontend uploads ~1 frame every 2 seconds during a question. The backend
returns the per-frame `FrameMetrics` for live UI feedback. When the answer is
submitted the frontend POSTs an aggregate dict (means/percentages) which we
persist to `Answer.vision_scores`. The scorer then folds those signals into
the `engagement` and `confidence` dimensions.

Graceful fallback
-----------------
If `mediapipe`/`opencv-python` aren't installed, every public function raises
`RuntimeError("Vision not available")`. The router catches that and returns
HTTP 503 with a friendly message — the rest of the app keeps working.
"""
from __future__ import annotations

import io
from dataclasses import dataclass, field
from threading import Lock

from loguru import logger


try:
    import cv2  # type: ignore
    import mediapipe as mp  # type: ignore
    import numpy as np  # type: ignore
    from PIL import Image  # type: ignore
    _AVAILABLE = True
except Exception:  # pragma: no cover
    cv2 = None  # type: ignore
    mp = None  # type: ignore
    np = None  # type: ignore
    Image = None  # type: ignore
    _AVAILABLE = False


_face_mesh = None
_lock = Lock()


# Six anchor points used for solvePnP head-pose estimation.
# These are FaceMesh landmark indices and the corresponding 3D model coords
# (in arbitrary mm units — only the relative geometry matters).
_PNP_LANDMARK_IDS = [1, 152, 33, 263, 61, 291]
_PNP_MODEL_3D = [
    (  0.0,    0.0,    0.0),     # 1   nose tip
    (  0.0,  -63.6,  -12.5),     # 152 chin
    (-43.3,   32.7,  -26.0),     # 33  left eye outer corner
    ( 43.3,   32.7,  -26.0),     # 263 right eye outer corner
    (-28.9,  -28.9,  -24.1),     # 61  left mouth corner
    ( 28.9,  -28.9,  -24.1),     # 291 right mouth corner
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_available() -> bool:
    """True iff MediaPipe + OpenCV + NumPy + Pillow imported successfully."""
    return _AVAILABLE


@dataclass
class FrameMetrics:
    face_detected: bool
    face_count: int
    head_yaw_deg: float | None = None        # left/right rotation
    head_pitch_deg: float | None = None      # up/down rotation
    head_roll_deg: float | None = None       # tilt
    gaze_x: float | None = None              # -1 (left)..+1 (right)
    gaze_y: float | None = None              # -1 (up)..+1 (down)
    eye_contact: bool | None = None          # True iff |gaze|, |yaw|, |pitch| small
    smile_score: float | None = None         # 0..1
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def analyze_frame(image_bytes: bytes) -> FrameMetrics:
    """
    Analyse a single JPEG/PNG/WebP frame.

    Raises RuntimeError if the CV stack isn't installed.
    """
    if not _AVAILABLE:
        raise RuntimeError(
            "Computer-vision dependencies are not installed. "
            "Install requirements-ml.txt to enable webcam analysis."
        )

    # Decode → numpy BGR
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Could not decode image: {exc}") from exc

    rgb = np.array(img)
    h, w = rgb.shape[:2]
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    fm = _get_face_mesh()
    res = fm.process(rgb)

    if not res.multi_face_landmarks:
        return FrameMetrics(face_detected=False, face_count=0,
                            notes=["No face detected in frame."])

    landmarks = res.multi_face_landmarks[0].landmark
    lm_xy = np.array([(p.x * w, p.y * h) for p in landmarks])

    # ---- Head pose -------------------------------------------------------
    yaw, pitch, roll = _head_pose(lm_xy, w, h)

    # ---- Gaze ------------------------------------------------------------
    gaze_x, gaze_y = _gaze_direction(lm_xy)

    # ---- Smile -----------------------------------------------------------
    smile = _smile_score(lm_xy)

    # ---- Eye contact derived signal -------------------------------------
    eye_contact = (
        abs(yaw) < 18 and abs(pitch) < 15
        and abs(gaze_x) < 0.35 and abs(gaze_y) < 0.35
    ) if (yaw is not None and pitch is not None and gaze_x is not None and gaze_y is not None) else None

    notes: list[str] = []
    if yaw is not None and abs(yaw) > 25:
        notes.append("Your head was turned away from the camera.")
    if pitch is not None and pitch > 20:
        notes.append("You were looking down.")
    if gaze_x is not None and abs(gaze_x) > 0.5:
        notes.append("Your eyes drifted off-screen.")

    return FrameMetrics(
        face_detected=True,
        face_count=len(res.multi_face_landmarks),
        head_yaw_deg=round(yaw, 1) if yaw is not None else None,
        head_pitch_deg=round(pitch, 1) if pitch is not None else None,
        head_roll_deg=round(roll, 1) if roll is not None else None,
        gaze_x=round(gaze_x, 3) if gaze_x is not None else None,
        gaze_y=round(gaze_y, 3) if gaze_y is not None else None,
        eye_contact=eye_contact,
        smile_score=round(smile, 3) if smile is not None else None,
        notes=notes,
    )


def aggregate_frames(frames: list[dict]) -> dict:
    """
    Aggregate a list of FrameMetrics dicts into a session-level vision summary.

    Returns dict with:
        face_present_pct      0..1
        eye_contact_pct       0..1   (only counted when face_detected)
        avg_head_yaw          mean(|yaw|) in degrees
        avg_head_pitch        mean(|pitch|) in degrees
        avg_smile             mean(smile_score) in 0..1
        engagement_score      0..10  composite ready for the scorer
        confidence_boost      0..1   (positive multiplier on the speech-only confidence)
        sample_count          number of frames
        notes                 list of observed issues
    """
    n = len(frames)
    if n == 0:
        return {
            "face_present_pct": None,
            "eye_contact_pct": None,
            "avg_head_yaw": None,
            "avg_head_pitch": None,
            "avg_smile": None,
            "engagement_score": None,
            "confidence_boost": None,
            "sample_count": 0,
            "notes": [],
        }

    face_n = sum(1 for f in frames if f.get("face_detected"))
    face_pct = face_n / n

    eye_n = sum(
        1 for f in frames
        if f.get("face_detected") and f.get("eye_contact") is True
    )
    eye_pct = (eye_n / face_n) if face_n else 0.0

    def _avg_abs(key):
        vals = [abs(f[key]) for f in frames if isinstance(f.get(key), (int, float))]
        return sum(vals) / len(vals) if vals else None

    avg_yaw = _avg_abs("head_yaw_deg")
    avg_pitch = _avg_abs("head_pitch_deg")

    smiles = [f["smile_score"] for f in frames if isinstance(f.get("smile_score"), (int, float))]
    avg_smile = sum(smiles) / len(smiles) if smiles else None

    # Engagement composite. Eye-contact only "counts" while the face is
    # visible, so we weight it by face_pct — otherwise a candidate could
    # be off-screen 70% of the time but still get high engagement just
    # because the few frames they appeared in had perfect eye contact.
    engagement = (
        face_pct * 5.0
        + (face_pct * eye_pct) * 4.0
        + (max(0.0, 1.0 - (avg_yaw or 0) / 40.0)) * 1.0
    )

    # Confidence boost: candidates who maintain eye contact appear more
    # confident. We expose a 0..1 multiplier the scorer can weave in.
    confidence_boost = 0.6 * eye_pct + 0.4 * face_pct

    notes: list[str] = []
    if face_pct < 0.7:
        notes.append(f"Face was visible only {round(face_pct * 100)}% of the time.")
    if eye_pct < 0.5 and face_pct >= 0.5:
        notes.append("You maintained eye contact less than half the time.")
    if avg_yaw is not None and avg_yaw > 18:
        notes.append("Your head turned away from the camera frequently.")

    return {
        "face_present_pct": round(face_pct, 3),
        "eye_contact_pct": round(eye_pct, 3),
        "avg_head_yaw": round(avg_yaw, 1) if avg_yaw is not None else None,
        "avg_head_pitch": round(avg_pitch, 1) if avg_pitch is not None else None,
        "avg_smile": round(avg_smile, 3) if avg_smile is not None else None,
        "engagement_score": round(min(10.0, engagement), 2),
        "confidence_boost": round(min(1.0, confidence_boost), 3),
        "sample_count": n,
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Internal — geometric helpers
# ---------------------------------------------------------------------------

def _get_face_mesh():
    global _face_mesh
    if _face_mesh is not None:
        return _face_mesh
    with _lock:
        if _face_mesh is not None:
            return _face_mesh
        logger.info("Loading MediaPipe FaceMesh (one-time)...")
        _face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,         # we hand it independent frames
            refine_landmarks=True,          # adds 10 iris landmarks
            max_num_faces=1,
            min_detection_confidence=0.5,
        )
        logger.info("✅ FaceMesh ready.")
        return _face_mesh


def _head_pose(lm: "np.ndarray", w: int, h: int):
    """Returns (yaw, pitch, roll) in degrees, or (None, None, None) on failure."""
    try:
        image_pts = np.array([lm[i] for i in _PNP_LANDMARK_IDS], dtype=np.float64)
        model_pts = np.array(_PNP_MODEL_3D, dtype=np.float64)
        focal = float(w)
        cam = np.array([
            [focal, 0,     w / 2.0],
            [0,     focal, h / 2.0],
            [0,     0,     1.0],
        ], dtype=np.float64)
        dist = np.zeros((4, 1))
        ok, rvec, _tvec = cv2.solvePnP(
            model_pts, image_pts, cam, dist, flags=cv2.SOLVEPNP_ITERATIVE
        )
        if not ok:
            return None, None, None
        rmat, _ = cv2.Rodrigues(rvec)
        # Convert rotation matrix to Euler angles
        sy = float(np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2))
        if sy >= 1e-6:
            pitch = float(np.degrees(np.arctan2(-rmat[2, 0], sy)))
            yaw = float(np.degrees(np.arctan2(rmat[1, 0], rmat[0, 0])))
            roll = float(np.degrees(np.arctan2(rmat[2, 1], rmat[2, 2])))
        else:
            pitch = float(np.degrees(np.arctan2(-rmat[2, 0], sy)))
            yaw = 0.0
            roll = float(np.degrees(np.arctan2(-rmat[1, 2], rmat[1, 1])))
        return yaw, pitch, roll
    except Exception:  # noqa: BLE001
        return None, None, None


def _gaze_direction(lm: "np.ndarray"):
    """
    Estimate gaze as iris-center displacement from eye-corner midpoint, in
    [-1..+1] coords (relative to eye width / height).
    """
    try:
        # Iris landmarks (refine_landmarks=True): left eye iris=468..472,
        # right eye iris=473..477. Eye corner indices (FaceMesh canonical):
        # left  outer=33, inner=133 ; right inner=362, outer=263.
        l_outer, l_inner = lm[33], lm[133]
        r_inner, r_outer = lm[362], lm[263]
        l_iris = lm[468:473].mean(axis=0)
        r_iris = lm[473:478].mean(axis=0)

        l_mid = (l_outer + l_inner) / 2
        r_mid = (r_inner + r_outer) / 2
        l_w = max(1.0, float(np.linalg.norm(l_inner - l_outer)))
        r_w = max(1.0, float(np.linalg.norm(r_outer - r_inner)))

        gx = ((l_iris[0] - l_mid[0]) / l_w + (r_iris[0] - r_mid[0]) / r_w) / 2
        gy = ((l_iris[1] - l_mid[1]) / l_w + (r_iris[1] - r_mid[1]) / r_w) / 2
        return float(gx), float(gy)
    except Exception:  # noqa: BLE001
        return None, None


def _smile_score(lm: "np.ndarray") -> float | None:
    """
    Heuristic smile detector: ratio of mouth width to mouth height,
    above a threshold suggests a smile/laugh; we blend with mouth-corner
    *upward* curvature.
    """
    try:
        left  = lm[61]    # left  mouth corner
        right = lm[291]   # right mouth corner
        upper = lm[13]    # upper lip middle
        lower = lm[14]    # lower lip middle
        width  = float(np.linalg.norm(left - right))
        height = max(1e-3, float(np.linalg.norm(upper - lower)))
        ratio = width / height                        # ~6 neutral, ~10+ smiling
        # Map ratio 5..12 to 0..1
        smile_from_ratio = max(0.0, min(1.0, (ratio - 5.0) / 7.0))

        # Corners curving upward = mouth corner y < lip baseline y
        baseline_y = (upper[1] + lower[1]) / 2
        avg_corner_y = (left[1] + right[1]) / 2
        upward = max(0.0, (baseline_y - avg_corner_y) / max(1e-3, height))
        smile_from_curve = max(0.0, min(1.0, upward * 2.0))

        return float(0.5 * smile_from_ratio + 0.5 * smile_from_curve)
    except Exception:  # noqa: BLE001
        return None
