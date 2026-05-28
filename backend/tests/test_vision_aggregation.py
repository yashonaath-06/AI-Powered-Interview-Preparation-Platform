"""
Tests for the vision aggregator. Pure-Python, no model needed.
"""
from app.services.vision_service import aggregate_frames


def _frame(face=True, yaw=0, pitch=0, gx=0.0, gy=0.0, eye_contact=True, smile=0.5):
    return {
        "face_detected": face,
        "face_count": 1 if face else 0,
        "head_yaw_deg": yaw if face else None,
        "head_pitch_deg": pitch if face else None,
        "head_roll_deg": 0,
        "gaze_x": gx if face else None,
        "gaze_y": gy if face else None,
        "eye_contact": eye_contact if face else None,
        "smile_score": smile if face else None,
    }


def test_empty_frames_returns_neutral():
    out = aggregate_frames([])
    assert out["sample_count"] == 0
    assert out["face_present_pct"] is None
    assert out["engagement_score"] is None


def test_perfect_engagement():
    frames = [_frame() for _ in range(10)]
    out = aggregate_frames(frames)
    assert out["face_present_pct"] == 1.0
    assert out["eye_contact_pct"] == 1.0
    assert out["engagement_score"] >= 9.0
    assert out["confidence_boost"] >= 0.95


def test_face_missing_half_the_time():
    frames = [_frame() for _ in range(5)] + [_frame(face=False) for _ in range(5)]
    out = aggregate_frames(frames)
    assert out["face_present_pct"] == 0.5
    assert out["engagement_score"] < 7.0
    assert any("Face was visible" in n for n in out["notes"])


def test_eye_contact_low_yields_note():
    frames = (
        [_frame(yaw=30, eye_contact=False, gx=0.6) for _ in range(8)]
        + [_frame(yaw=2,  eye_contact=True) for _ in range(2)]
    )
    out = aggregate_frames(frames)
    assert out["eye_contact_pct"] <= 0.30
    assert out["engagement_score"] < 7.0
    assert any("eye contact" in n.lower() for n in out["notes"])


def test_high_yaw_yields_head_turn_note():
    frames = [_frame(yaw=35, eye_contact=False) for _ in range(10)]
    out = aggregate_frames(frames)
    assert out["avg_head_yaw"] is not None and out["avg_head_yaw"] >= 30
    assert any("head turned" in n.lower() for n in out["notes"])
