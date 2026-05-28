"""
Resume analysis pipeline.

Steps for an uploaded PDF:

    1. Extract raw text via pypdf (no system deps, pure Python)
    2. Detect structural sections (Experience / Education / Skills / Projects)
    3. Match the text against a curated 100+ skill taxonomy
       (regex word-boundary alias matching)
    4. Compare against the user's target_role:
         - Hard match  : intersection with role's known skill hints
         - Semantic match: sentence-transformers cosine similarity
                           (only if Phase-9 NLP deps are installed)
    5. Compute a 0-100 match_score
    6. Produce LLM-written improvement feedback (Groq) with a
       templated fallback when no key is configured

The service falls back gracefully when optional deps aren't installed:
    - pypdf missing  -> raises 503 (caller responsibility)
    - sentence-transformers missing -> only literal/keyword matching used
"""
from __future__ import annotations

import io
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from app.services import llm_service, nlp_service

try:
    from pypdf import PdfReader  # type: ignore
    _PDF_AVAILABLE = True
except Exception:  # pragma: no cover
    PdfReader = None  # type: ignore
    _PDF_AVAILABLE = False


_TAXONOMY_PATH = Path(__file__).parent.parent / "data" / "skills_taxonomy.json"
_taxonomy: dict | None = None


# ---------------------------------------------------------------------------
# Public capability flag
# ---------------------------------------------------------------------------

def is_available() -> bool:
    """True iff pypdf is importable. The rest is pure Python."""
    return _PDF_AVAILABLE


@dataclass
class AnalyzedResume:
    raw_text: str
    word_count: int
    detected_sections: list[str]
    parsed_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    skill_categories: dict[str, list[str]]
    target_role: str | None
    match_score: float
    semantic_score: float | None
    ai_feedback: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {**self.__dict__}


# ---------------------------------------------------------------------------
# PDF extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    if not _PDF_AVAILABLE:
        raise RuntimeError(
            "pypdf is not installed on this server. "
            "Install requirements.txt to enable resume parsing."
        )

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Could not open PDF: {exc}") from exc

    chunks: list[str] = []
    for page in reader.pages:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001
            continue
    return "\n".join(chunks).strip()


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------

_SECTION_PATTERNS = {
    "Experience":     r"\b(experience|work history|employment|professional experience)\b",
    "Education":      r"\b(education|academic|qualifications)\b",
    "Skills":         r"\b(skills|technical skills|technologies)\b",
    "Projects":       r"\b(projects|personal projects|side projects)\b",
    "Certifications": r"\b(certifications|certificates|courses)\b",
    "Achievements":   r"\b(achievements|awards|accomplishments|honors)\b",
    "Summary":        r"\b(summary|profile|objective|career objective|about me)\b",
    "Contact":        r"\b(contact|email|phone|linkedin|github)\b",
}


def detect_sections(text: str) -> list[str]:
    lo = text.lower()
    return [name for name, pat in _SECTION_PATTERNS.items() if re.search(pat, lo)]


# ---------------------------------------------------------------------------
# Skill matching
# ---------------------------------------------------------------------------

def _load_taxonomy() -> dict:
    global _taxonomy
    if _taxonomy is None:
        with _TAXONOMY_PATH.open("r", encoding="utf-8") as f:
            _taxonomy = json.load(f)
    return _taxonomy


def _match_skills_in_text(text: str) -> tuple[list[str], dict[str, list[str]]]:
    tax = _load_taxonomy()
    lo = "\n" + text.lower() + "\n"
    found: list[str] = []
    cats: dict[str, list[str]] = {}

    for entry in tax["skills"]:
        canonical = entry["name"]
        category  = entry.get("category", "other")
        for alias in entry["aliases"]:
            if re.search(rf"(?<![a-zA-Z0-9_+#]){alias}(?![a-zA-Z0-9_+#])", lo):
                found.append(canonical)
                cats.setdefault(category, []).append(canonical)
                break

    seen: set[str] = set()
    deduped = [s for s in found if not (s in seen or seen.add(s))]
    return deduped, cats


def _expected_skills_for_role(target_role: str | None) -> list[str]:
    if not target_role:
        return []
    tax = _load_taxonomy()
    hints = tax.get("_role_skill_hints", {})
    target_lo = target_role.strip().lower()
    if target_lo in {k.lower() for k in hints.keys()}:
        for k in hints:
            if k.lower() == target_lo:
                return hints[k]
    for k, v in hints.items():
        if k.lower() in target_lo or target_lo in k.lower():
            return v
    return []


# ---------------------------------------------------------------------------
# Match score
# ---------------------------------------------------------------------------

def _compute_match_score(
    parsed: list[str],
    expected: list[str],
    semantic: float | None,
    word_count: int,
    section_count: int,
) -> float:
    if not expected:
        completeness = min(1.0, word_count / 350.0)
        section_pct  = min(1.0, section_count / 4.0)
        return round(60 + completeness * 25 + section_pct * 15, 1)

    parsed_set   = {s.lower() for s in parsed}
    expected_set = {s.lower() for s in expected}
    overlap = parsed_set & expected_set
    coverage = len(overlap) / len(expected_set)

    completeness = min(1.0, word_count / 350.0)
    sem_bonus = float(semantic) * 15 if semantic is not None else 0.0

    score = (
        coverage * 60.0
        + completeness * 20.0
        + min(section_count / 5.0, 1.0) * 5.0
        + sem_bonus
    )
    return round(min(100.0, score), 1)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_resume(
    pdf_bytes: bytes,
    *,
    target_role: str | None = None,
) -> AnalyzedResume:
    raw_text = extract_text_from_pdf(pdf_bytes)
    if not raw_text or len(raw_text) < 50:
        raise ValueError(
            "Could not extract enough text from this PDF. "
            "If your resume is image-only, please upload a text-based PDF."
        )

    sections = detect_sections(raw_text)
    parsed, cats = _match_skills_in_text(raw_text)

    expected = _expected_skills_for_role(target_role)
    matched = [s for s in parsed if s.lower() in {e.lower() for e in expected}] if expected else parsed[:]
    missing = [s for s in expected if s.lower() not in {p.lower() for p in parsed}] if expected else []

    semantic: float | None = None
    if target_role and nlp_service.is_semantic_available():
        role_doc = (
            f"A strong {target_role} candidate has experience with: "
            f"{', '.join(expected) if expected else target_role}."
        )
        semantic = nlp_service.semantic_similarity(raw_text[:3000], role_doc)

    word_count = len(raw_text.split())
    score = _compute_match_score(parsed, expected, semantic, word_count, len(sections))

    notes: list[str] = []
    if word_count < 200:
        notes.append("Resume seems short — aim for ~400-700 words for technical roles.")
    if "Skills" not in sections:
        notes.append("Add an explicit Skills section to make scanning easier.")
    if "Projects" not in sections:
        notes.append("Add a Projects section showcasing 2-3 substantial pieces of work.")
    if expected and len(missing) > len(expected) * 0.6:
        notes.append(
            f"You're missing many key skills for {target_role!r}. "
            f"Consider adding hands-on examples for: {', '.join(missing[:5])}."
        )

    feedback = _generate_feedback(
        raw_text=raw_text,
        target_role=target_role,
        parsed=parsed,
        matched=matched,
        missing=missing,
        sections=sections,
        notes=notes,
    )

    return AnalyzedResume(
        raw_text=raw_text,
        word_count=word_count,
        detected_sections=sections,
        parsed_skills=parsed,
        matched_skills=matched,
        missing_skills=missing,
        skill_categories=cats,
        target_role=target_role,
        match_score=score,
        semantic_score=round(semantic, 3) if semantic is not None else None,
        ai_feedback=feedback,
        notes=notes,
    )


def _generate_feedback(
    *,
    raw_text: str,
    target_role: str | None,
    parsed: list[str],
    matched: list[str],
    missing: list[str],
    sections: list[str],
    notes: list[str],
) -> str:
    payload = {
        "target_role": target_role,
        "parsed_skills": parsed,
        "matched_skills": matched,
        "missing_skills": missing,
        "sections": sections,
        "notes": notes,
        "resume_excerpt": raw_text[:1500],
    }

    if llm_service.is_available():
        text = llm_service.chat_text(
            system=(
                "You are an expert career coach reviewing a candidate's resume "
                "against a target role. Write 4-6 short paragraphs of friendly, "
                "specific, actionable feedback covering: (1) overall first impression, "
                "(2) one or two strengths, (3) two concrete weaknesses or gaps, "
                "(4) which 3-5 missing skills are highest priority and how to gain "
                "them quickly, (5) one tactical formatting/wording suggestion, "
                "(6) one motivating closing line. Do NOT repeat the JSON; speak "
                "directly to the candidate as 'you'."
            ),
            user=json.dumps(payload),
        )
        if text:
            return text.strip()

    # ---- Templated fallback ----
    lines: list[str] = []
    if target_role:
        lines.append(f"Reviewing your resume for the role of **{target_role}**.")
    else:
        lines.append("Reviewing your resume (no target role specified).")

    if matched:
        lines.append(
            f"Strengths: you already demonstrate {len(matched)} of the most relevant "
            f"skills — including {', '.join(matched[:5])}."
        )
    if missing:
        top_missing = ', '.join(missing[:5])
        lines.append(
            f"Key gaps: consider adding hands-on experience with {top_missing}. "
            "Even a personal project per gap goes a long way."
        )
    if "Projects" not in sections:
        lines.append(
            "Tip: add a Projects section with 2-3 substantial entries (1 line of context, "
            "1-2 lines of measurable impact, 1 line of tech stack)."
        )
    lines.append(
        "Use action verbs (built, shipped, led, optimized) and quantify everything "
        "(\"reduced API latency by 40%\", \"shipped feature used by 12k DAU\")."
    )
    lines.append("Keep going — small targeted improvements compound quickly. 🚀")
    return "\n\n".join(lines)
