"""
Tests for the Phase-9 scorer.

The scorer must produce sensible scores **with or without** the heavy ML
deps installed. These tests focus on relative behaviour so they pass in
both modes.
"""
from app.services.scoring_service import score_answer


GOOD_ANSWER_DP = (
    "Dynamic programming solves problems that have overlapping subproblems "
    "and optimal substructure. We avoid recomputing the same subproblem by "
    "either memoizing top-down or building a tabulation bottom-up. Classic "
    "examples include Fibonacci and the knapsack problem."
)
BAD_ANSWER = "Um, like, I dont really know."
DP_KEYWORDS = ["overlapping subproblems", "optimal substructure", "memoization", "tabulation", "knapsack"]
DP_SAMPLE = (
    "Dynamic programming applies when problems have overlapping subproblems "
    "and optimal substructure. We use memoization or tabulation."
)


def test_good_answer_outscores_bad_answer_overall():
    good = score_answer(GOOD_ANSWER_DP, DP_KEYWORDS, sample_answer=DP_SAMPLE)
    bad = score_answer(BAD_ANSWER, DP_KEYWORDS, sample_answer=DP_SAMPLE)
    assert good.overall > bad.overall, (good.overall, bad.overall)


def test_filler_words_lower_confidence():
    no_filler = score_answer(
        "I built a chat application using WebSockets and deployed it on AWS.",
        expected_keywords=None,
    )
    with_filler = score_answer(
        "Um, like, I built a, you know, chat application using, basically, WebSockets and, like, deployed it on AWS.",
        expected_keywords=None,
    )
    assert with_filler.confidence < no_filler.confidence


def test_empty_answer_is_zero():
    s = score_answer("", DP_KEYWORDS)
    assert s.overall == 0
    assert "No answer" in s.notes[0]


def test_too_short_answer_gets_a_note():
    s = score_answer("Yes.", DP_KEYWORDS)
    assert any("short" in n.lower() for n in s.notes)
    assert s.engagement <= 5.0


def test_components_diagnostics_present():
    s = score_answer(GOOD_ANSWER_DP, DP_KEYWORDS, sample_answer=DP_SAMPLE)
    c = s.components
    assert "word_count" in c
    assert c["word_count"] >= 30
    assert "literal_keyword_coverage" in c
    assert 0.0 <= c["literal_keyword_coverage"] <= 1.0


def test_keyword_coverage_drives_technical_score():
    keywords = ["sharding", "replication", "partition", "consensus"]
    bare_mention = score_answer("I would shard the database.", keywords)
    full_coverage = score_answer(
        "I would use sharding for horizontal partitioning, replication for "
        "availability, and a Raft-based consensus protocol for consistency.",
        keywords,
    )
    assert full_coverage.technical > bare_mention.technical


def test_aggregate_returns_zeroes_for_empty():
    from app.services.scoring_service import aggregate_session_scores
    out = aggregate_session_scores([])
    assert out["overall"] == 0 and out["answers_scored"] == 0


def test_aggregate_averages_dimensions():
    from app.services.scoring_service import aggregate_session_scores
    out = aggregate_session_scores([
        {"technical": 8, "communication": 7, "confidence": 6, "engagement": 5, "overall": 7},
        {"technical": 4, "communication": 5, "confidence": 4, "engagement": 5, "overall": 4.5},
    ])
    assert out["technical"] == 6.0
    assert out["overall"] == 5.75
    assert out["answers_scored"] == 2
