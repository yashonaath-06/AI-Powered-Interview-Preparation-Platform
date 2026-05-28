"""
Phase-9 answer scorer.

Pipeline
--------
Every answer is graded along **four dimensions**, each on a 0-10 scale:

    technical      — content correctness vs. the expected/sample answer
    communication  — clarity, length-appropriateness, readability
    confidence     — fluency, lack of filler/hedging language
    engagement     — substance: vocabulary diversity + length

The scorer combines:
    1. Heuristic features (always available):
         length, filler/hedging counts, vocabulary diversity.
    2. NLP signals (when sentence-transformers + textstat installed):
         semantic_similarity (vs. sample_answer / question_text),
         soft keyword alignment, Flesch reading-ease.

Design goal: produces sensible scores **with or without** the heavy ML
deps installed. When NLP signals are present they outweigh heuristics.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.services import nlp_service


# ---- Lexical features ------------------------------------------------------

FILLER_WORDS = {
    "um", "uh", "umm", "uhh", "er", "ah", "like", "basically",
    "actually", "literally", "you know", "i mean", "sort of",
    "kind of", "i guess",
}
HEDGING_WORDS = {"maybe", "perhaps", "i think", "i guess", "kind of", "sort of"}


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _filler_count(text: str) -> int:
    """Count filler words/phrases. Punctuation-tolerant."""
    # Replace non-word, non-space characters with spaces so we can use
    # whitespace-padded substring matching.
    cleaned = " " + re.sub(r"[^\w\s]", " ", text.lower()) + " "
    cleaned = re.sub(r"\s+", " ", cleaned)
    return sum(cleaned.count(f" {f} ") for f in FILLER_WORDS)


def _hedging_count(text: str) -> int:
    cleaned = " " + re.sub(r"[^\w\s]", " ", text.lower()) + " "
    cleaned = re.sub(r"\s+", " ", cleaned)
    # Hedging phrases may include spaces, so use the cleaned single-space
    # form as the haystack.
    return sum(cleaned.count(f" {h} ") for h in HEDGING_WORDS)


# ---- Sub-score helpers -----------------------------------------------------

def _length_score(wc: int) -> tuple[float, str | None]:
    """Returns (score 0-10, optional note)."""
    if wc < 10:
        return 2.5, "Your answer was very short — try to elaborate with examples."
    if wc < 30:
        return 5.0, "Your answer could be more detailed."
    if wc <= 200:
        return 9.0, None
    if wc <= 350:
        return 7.5, "Your answer was a bit long; try to be more concise."
    return 6.0, "Your answer was very long; aim for 1-2 minutes of speech."


def _literal_keyword_coverage(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    text_lo = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lo)
    return hits / len(keywords)


def _readability_to_score(raw: float | None) -> float | None:
    """
    Map Flesch reading-ease (0-100, higher = easier) to a 0-10 communication
    sub-score. We reward readings in 50..80 (conversational).
    """
    if raw is None:
        return None
    if raw >= 70:
        return 9.5
    if raw >= 50:
        return 8.5
    if raw >= 30:
        return 6.5
    if raw >= 10:
        return 4.5
    return 2.5


# ---- Public API ------------------------------------------------------------

@dataclass
class AnswerScore:
    technical: float
    communication: float
    confidence: float
    engagement: float
    overall: float
    notes: list[str]
    components: dict  # diagnostic detail (used by tests + admin UI)

    def to_dict(self) -> dict:
        return {
            "technical": round(self.technical, 2),
            "communication": round(self.communication, 2),
            "confidence": round(self.confidence, 2),
            "engagement": round(self.engagement, 2),
            "overall": round(self.overall, 2),
            "notes": self.notes,
            "components": self.components,
        }


def score_answer(
    answer_text: str,
    expected_keywords: list[str] | None = None,
    *,
    sample_answer: str | None = None,
    question_text: str | None = None,
    vision_summary: dict | None = None,
) -> AnswerScore:
    """
    Score one answer along 4 dimensions.

    Parameters
    ----------
    answer_text : the candidate's answer (transcript or typed)
    expected_keywords : list of keywords the answer should ideally cover
    sample_answer : optional reference / model answer (Phase 7 question_bank
        already ships these for many questions)
    question_text : the question itself; used as a fallback semantic
        reference when no sample_answer is available
    vision_summary : optional Phase-10 aggregate of webcam frame metrics
        (face_present_pct, eye_contact_pct, engagement_score, …). When
        present the engagement and confidence sub-scores fold it in.
    """
    text = (answer_text or "").strip()
    notes: list[str] = []
    components: dict = {}

    if not text:
        return AnswerScore(0, 0, 0, 0, 0, ["No answer was given."], components)

    wc = _word_count(text)
    components["word_count"] = wc

    # ---- Length ---------------------------------------------------------
    length_score, length_note = _length_score(wc)
    if length_note:
        notes.append(length_note)
    components["length_score"] = length_score

    # ---- Filler / hedging ----------------------------------------------
    fillers = _filler_count(text)
    hedges = _hedging_count(text)
    components["filler_count"] = fillers
    components["hedging_count"] = hedges
    if fillers >= 3:
        notes.append(f"Detected {fillers} filler words — try to slow down.")

    # ---- Keyword coverage ---------------------------------------------
    literal_cov = _literal_keyword_coverage(text, expected_keywords or [])
    soft_cov = nlp_service.best_keyword_alignment(text, expected_keywords or [])
    components["literal_keyword_coverage"] = round(literal_cov, 3)
    if soft_cov is not None:
        components["semantic_keyword_coverage"] = round(soft_cov, 3)

    if expected_keywords:
        # Combine literal + (if available) semantic coverage; semantic wins
        # because it's more forgiving of paraphrasing.
        coverage = soft_cov if soft_cov is not None else literal_cov
        if coverage < 0.4:
            notes.append(
                f"You covered roughly {round(coverage*100)}% of the expected concepts "
                "— consider mentioning more relevant terms."
            )
        keyword_score = round(coverage * 10, 2)
    else:
        keyword_score = 7.0  # neutral baseline if no keywords

    # ---- Semantic similarity vs. reference ------------------------------
    reference = sample_answer or question_text
    sem_sim = nlp_service.semantic_similarity(text, reference) if reference else None
    if sem_sim is not None:
        components["semantic_similarity"] = round(sem_sim, 3)
        if sample_answer and sem_sim < 0.30:
            notes.append(
                "Your answer is semantically distant from the model answer — "
                "you may have misunderstood the question."
            )
    sem_score = sem_sim * 10 if sem_sim is not None else None

    # ---- Readability ---------------------------------------------------
    flesch = nlp_service.readability(text)
    read_score = _readability_to_score(flesch)
    if flesch is not None:
        components["flesch_reading_ease"] = round(flesch, 1)

    # ---- Vocabulary diversity ------------------------------------------
    vocab = nlp_service.vocabulary_diversity(text)
    components["vocabulary_diversity"] = round(vocab, 3)
    vocab_score = round(min(10.0, vocab * 18 + 2.0), 2)

    # ---- Compose 4 dimensions ------------------------------------------
    if sem_score is not None:
        # NLP available: 60% semantic, 30% keyword, 10% length
        technical = 0.60 * sem_score + 0.30 * keyword_score + 0.10 * length_score
    else:
        # Fallback: 70% keyword, 30% length
        technical = 0.70 * keyword_score + 0.30 * length_score

    if read_score is not None:
        # 50% length, 30% fluency, 20% readability
        fluency_score = max(2.0, 10.0 - fillers * 0.8)
        communication = 0.50 * length_score + 0.30 * fluency_score + 0.20 * read_score
    else:
        fluency_score = max(2.0, 10.0 - fillers * 0.8)
        communication = 0.50 * length_score + 0.50 * fluency_score

    confidence = max(2.0, 10.0 - hedges * 0.6 - fillers * 0.4)

    # Engagement: substance via length + vocab diversity
    engagement = 0.50 * length_score + 0.50 * vocab_score
    if wc < 30:
        engagement = min(engagement, 5.0)

    # ---- Vision blending (Phase 10) ------------------------------------
    if vision_summary and vision_summary.get("sample_count", 0) > 0:
        vision_engagement = vision_summary.get("engagement_score")
        if isinstance(vision_engagement, (int, float)):
            # 60% lexical engagement, 40% camera-derived engagement
            engagement = 0.60 * engagement + 0.40 * float(vision_engagement)
            components["vision_engagement"] = round(float(vision_engagement), 2)

        boost = vision_summary.get("confidence_boost")
        if isinstance(boost, (int, float)):
            # Multiplier: maintaining good eye contact lifts confidence up to +30%
            multiplier = 1.0 + (float(boost) - 0.5) * 0.6
            confidence = max(1.0, min(10.0, confidence * multiplier))
            components["vision_confidence_boost"] = round(float(boost), 3)

        for n in vision_summary.get("notes", []) or []:
            notes.append(n)
        components["vision_face_present_pct"] = vision_summary.get("face_present_pct")
        components["vision_eye_contact_pct"] = vision_summary.get("eye_contact_pct")

    overall = (
        technical * 0.40 + communication * 0.25 + confidence * 0.20 + engagement * 0.15
    )

    return AnswerScore(
        technical=round(technical, 2),
        communication=round(communication, 2),
        confidence=round(confidence, 2),
        engagement=round(engagement, 2),
        overall=round(overall, 2),
        notes=notes,
        components=components,
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
