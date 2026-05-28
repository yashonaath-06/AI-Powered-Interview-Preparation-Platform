"""
NLP utilities — semantic similarity and readability.

Why this exists
---------------
Phase 7 shipped a heuristic scorer (keyword coverage, length, filler-word
penalties). That works but it doesn't understand *meaning*. This module
adds two real-NLP signals:

    semantic_similarity(a, b) -> float in [0, 1]
        Cosine similarity between sentence-transformer embeddings of the
        candidate's answer and the reference answer / question. Captures
        "did the candidate actually answer the question" without requiring
        word-for-word matches.

    readability(text) -> float in [0, 100]
        Flesch reading-ease: higher = easier to read. We translate this
        into a [0, 10] communication-clarity sub-score.

Graceful fallback
-----------------
If `sentence-transformers` / `textstat` aren't installed, every public
function returns `None`. The scorer in `scoring_service.py` checks for
`None` and skips that signal, blending only the available ones.
"""
from __future__ import annotations

from threading import Lock

from loguru import logger


# ---- sentence-transformers (heavy — optional) ------------------------------
try:
    from sentence_transformers import SentenceTransformer, util  # type: ignore
    import numpy as np  # type: ignore
    _ST_AVAILABLE = True
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore
    util = None  # type: ignore
    np = None  # type: ignore
    _ST_AVAILABLE = False


# ---- textstat (small, pure Python) -----------------------------------------
try:
    import textstat  # type: ignore
    _TS_AVAILABLE = True
except Exception:  # pragma: no cover
    textstat = None  # type: ignore
    _TS_AVAILABLE = False


_model = None
_model_lock = Lock()
_DEFAULT_MODEL = "all-MiniLM-L6-v2"  # ~80 MB, fast on CPU, English-strong


# ---------------------------------------------------------------------------
# Capability flags
# ---------------------------------------------------------------------------

def is_semantic_available() -> bool:
    """True iff sentence-transformers can be used."""
    return _ST_AVAILABLE


def is_readability_available() -> bool:
    """True iff textstat is installed."""
    return _TS_AVAILABLE


# ---------------------------------------------------------------------------
# Semantic similarity
# ---------------------------------------------------------------------------

def semantic_similarity(text_a: str, text_b: str) -> float | None:
    """Cosine similarity in [0, 1]; None if sentence-transformers missing."""
    if not _ST_AVAILABLE:
        return None
    a = (text_a or "").strip()
    b = (text_b or "").strip()
    if not a or not b:
        return None

    model = _get_model()
    embeds = model.encode([a, b], convert_to_tensor=True, normalize_embeddings=True)
    sim = float(util.cos_sim(embeds[0], embeds[1]).item())
    # cos_sim is [-1, 1]; for natural-language paraphrase tasks it's
    # almost always 0..1, but clamp defensively.
    return max(0.0, min(1.0, sim))


def best_keyword_alignment(answer: str, keywords: list[str]) -> float | None:
    """
    Soft keyword-coverage: average semantic similarity between the answer
    and each expected keyword/phrase.

    More forgiving than literal substring matching — "constant time" still
    matches the keyword "O(1)", "polymorphism" still matches "ad-hoc".
    """
    if not _ST_AVAILABLE or not answer or not keywords:
        return None

    model = _get_model()
    ans_emb = model.encode(answer, convert_to_tensor=True, normalize_embeddings=True)
    kw_embs = model.encode(keywords, convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(ans_emb, kw_embs)[0]  # tensor of len(keywords)
    # We treat anything above 0.4 as "covered". Average coverage over all kws.
    covered = (sims > 0.40).float().mean().item()
    return float(covered)


# ---------------------------------------------------------------------------
# Readability
# ---------------------------------------------------------------------------

def readability(text: str) -> float | None:
    """
    Flesch reading-ease, clipped to [0, 100]. Higher = easier to read.

    Conversational interview answers tend to score 60-80; very dense,
    jargon-heavy answers score lower.
    """
    if not _TS_AVAILABLE:
        return None
    text = (text or "").strip()
    if not text:
        return 0.0

    raw = textstat.flesch_reading_ease(text)
    return float(max(0.0, min(100.0, raw)))


def vocabulary_diversity(text: str) -> float:
    """
    Type-token ratio: unique_words / total_words. Always available.
    Returns 0..1; ~0.5 is healthy for an interview answer.
    """
    words = [w.lower() for w in (text or "").split() if w.isalpha()]
    if len(words) < 5:
        return 0.0
    return len(set(words)) / len(words)


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _get_model():
    """Lazy-load the sentence-transformer model in a thread-safe way."""
    global _model
    if _model is not None:
        return _model
    with _model_lock:
        if _model is not None:
            return _model
        logger.info(
            f"Loading sentence-transformer {_DEFAULT_MODEL!r} (one-time)..."
        )
        _model = SentenceTransformer(_DEFAULT_MODEL)
        logger.info("✅ NLP semantic model ready.")
        return _model
