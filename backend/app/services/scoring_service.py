"""
Baseline answer scorer.

Used by the interview engine in Phase 7 to give every answer a 0-10 score
across four dimensions:

    technical     — keyword coverage vs. the question's expected_keywords
    communication — length-appropriateness + filler-word penalty
    confidence    — fluency proxy (filler words, hedging language)
    engagement    — substantive length proxy

Phase 9 will replace this with real NLP (sentence-transformers + grammar
checking) and Phase 10 will fold in vision-derived signals. The function
signature stays the same, so callers don't need to change.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


FILLER_WORDS = {
    "um", "uh", "umm", "uhh", "er", "ah", "like", "basically",
    "actually", "literally", "you know", "i mean", "sort of",
    "kind of", "i guess",
}
HEDGING_WORDS = {"maybe", "perhaps", "i think", "i guess", "kind of", "sort of"}


@dataclass
class AnswerScore:
    technical: float
    communication: float
    confidence: float
    engagement: float
    overall: float
    notes: list[str]

    def to_dict(self) -> dict:
        return {
            "technical": round(self.technical, 2),
            "communication": round(self.communication, 2),
            "confidence": round(self.confidence, 2),
            "engagement": round(self.engagement, 2),
            "overall": round(self.overall, 2),
            "notes": self.notes,
        }


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _filler_count(text: str) -> int:
    lo = " " + text.lower() + " "
    return sum(lo.count(f" {f} ") for f in FILLER_WORDS)


def score_answer(
    answer_text: str,
    expected_keywords: list[str] | None = None,
) -> AnswerScore:
    """
    Score an answer 0-10 across four dimensions.

    Returns an AnswerScore dataclass with `.to_dict()` for JSON serialisation.
    """
    text = (answer_text or "").strip()
    notes: list[str] = []

    if not text:
        notes.append("No answer was given.")
        return AnswerScore(0, 0, 0, 0, 0, notes)

    wc = _word_count(text)

    # ---- Length sub-score (sweet spot 50-180 words) ---------------------
    if wc < 10:
        length_score = 2.5
        notes.append("Your answer was very short — try to elaborate with examples.")
    elif wc < 30:
        length_score = 5.0
        notes.append("Your answer could be more detailed.")
    elif wc <= 200:
        length_score = 9.0
    elif wc <= 350:
        length_score = 7.5
        notes.append("Your answer was a bit long; try to be more concise.")
    else:
        length_score = 6.0
        notes.append("Your answer was very long; aim for 1-2 minutes of speech.")

    # ---- Keyword coverage ----------------------------------------------
    if expected_keywords:
        text_lo = text.lower()
        hits = sum(1 for kw in expected_keywords if kw.lower() in text_lo)
        coverage = hits / max(1, len(expected_keywords))
        keyword_score = round(coverage * 10, 2)
        if coverage < 0.4:
            notes.append(
                f"You covered {hits}/{len(expected_keywords)} key concepts — "
                "consider mentioning more relevant terms."
            )
    else:
        keyword_score = 7.0  # no keywords known, neutral baseline

    # ---- Fluency / fillers ---------------------------------------------
    fillers = _filler_count(text)
    fluency_score = max(2.0, 10.0 - fillers * 0.8)
    if fillers >= 3:
        notes.append(f"Detected {fillers} filler words — try to slow down.")

    # ---- Hedging / confidence -----------------------------------------
    hedges = sum(text.lower().count(h) for h in HEDGING_WORDS)
    confidence = max(2.0, 10.0 - hedges * 0.6 - fillers * 0.4)

    # ---- Compose dimensions --------------------------------------------
    technical = round((keyword_score * 0.7 + length_score * 0.3), 2)
    communication = round((length_score * 0.5 + fluency_score * 0.5), 2)
    engagement = round(min(10.0, length_score * 0.6 + 4.0 if wc >= 30 else length_score), 2)

    overall = round(
        technical * 0.40 + communication * 0.25 + confidence * 0.20 + engagement * 0.15,
        2,
    )

    return AnswerScore(
        technical=technical,
        communication=communication,
        confidence=round(confidence, 2),
        engagement=engagement,
        overall=overall,
        notes=notes,
    )


def aggregate_session_scores(answer_score_dicts: list[dict]) -> dict:
    """Average all per-answer score dicts into a session-level summary."""
    if not answer_score_dicts:
        return {
            "technical": 0,
            "communication": 0,
            "confidence": 0,
            "engagement": 0,
            "overall": 0,
            "answers_scored": 0,
        }
    keys = ["technical", "communication", "confidence", "engagement", "overall"]
    n = len(answer_score_dicts)
    out = {k: round(sum(s.get(k, 0) for s in answer_score_dicts) / n, 2) for k in keys}
    out["answers_scored"] = n
    return out
