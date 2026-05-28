"""
Tests for the Phase-10 vision-aware scoring path.
"""
from app.services.scoring_service import score_answer


GOOD = (
    "I would design YouTube's recommendation system as a two-stage funnel: "
    "candidate generation using collaborative filtering and embeddings, then "
    "ranking with a deep neural network on watch history features. We'd run "
    "ongoing AB tests for evaluation."
)
KEYWORDS = ["candidate generation", "ranking", "embeddings", "watch history", "AB test"]


def test_vision_engaged_lifts_engagement_above_no_vision():
    no_vision = score_answer(GOOD, KEYWORDS)
    with_vision = score_answer(
        GOOD, KEYWORDS,
        vision_summary={
            "sample_count": 20,
            "face_present_pct": 1.0,
            "eye_contact_pct": 1.0,
            "engagement_score": 10.0,
            "confidence_boost": 1.0,
            "notes": [],
        },
    )
    assert with_vision.engagement >= no_vision.engagement
    assert with_vision.confidence >= no_vision.confidence


def test_vision_disengaged_lowers_engagement():
    base = score_answer(GOOD, KEYWORDS)
    bad = score_answer(
        GOOD, KEYWORDS,
        vision_summary={
            "sample_count": 20,
            "face_present_pct": 0.3,
            "eye_contact_pct": 0.1,
            "engagement_score": 1.5,
            "confidence_boost": 0.15,
            "notes": ["Face was visible only 30% of the time."],
        },
    )
    assert bad.engagement < base.engagement
    assert bad.confidence < base.confidence
    assert any("face was visible" in n.lower() for n in bad.notes)


def test_zero_samples_skips_vision():
    a = score_answer(GOOD, KEYWORDS, vision_summary={"sample_count": 0})
    b = score_answer(GOOD, KEYWORDS)
    # A vision summary with no samples should not change the score.
    assert a.engagement == b.engagement
    assert a.confidence == b.confidence
