"""Resume analyzer tests."""
import io

import pytest


def _generate_pdf() -> bytes:
    """Build a tiny text-based PDF in-memory using reportlab if available;
    else skip the test gracefully."""
    try:
        from reportlab.pdfgen import canvas  # type: ignore
    except Exception:
        pytest.skip("reportlab not installed; skipping PDF integration test")

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    y = 800
    for line in [
        "John Doe — Software Engineer",
        "SKILLS",
        "Python, JavaScript, TypeScript, React, Next.js, Node.js, FastAPI",
        "PostgreSQL, MongoDB, Docker, Git, AWS, REST, Data Structures, Algorithms",
        "PROJECTS",
        "AI Interview Prep — full-stack platform with Whisper STT and MediaPipe vision",
        "EXPERIENCE",
        "Software Intern at Acme Corp — built REST APIs in Python and React frontend",
        "EDUCATION",
        "B.Tech Computer Science, IIT Delhi",
    ]:
        c.drawString(50, y, line); y -= 18
    c.save()
    buf.seek(0)
    return buf.read()


def test_resume_analysis_extracts_skills(client, make_user):
    u = make_user()
    pdf = _generate_pdf()
    r = client.post(
        "/api/resume/analyze",
        headers=u["auth"],
        files={"resume": ("john.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"target_role": "Software Engineer"},
    )
    assert r.status_code == 201, r.text
    out = r.json()
    assert "Python" in out["parsed_skills"]
    assert "React" in out["parsed_skills"]
    assert out["match_score"] > 0
    assert "Skills" in out["detected_sections"]
    assert out["ai_feedback"]


def test_resume_non_pdf_rejected(client, make_user):
    u = make_user()
    r = client.post(
        "/api/resume/analyze",
        headers=u["auth"],
        files={"resume": ("note.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert r.status_code == 400


def test_resume_list_and_delete(client, make_user):
    u = make_user()
    pdf = _generate_pdf()
    r = client.post(
        "/api/resume/analyze",
        headers=u["auth"],
        files={"resume": ("john.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"target_role": "Software Engineer"},
    )
    rid = r.json()["id"]

    listed = client.get("/api/resume", headers=u["auth"])
    assert listed.status_code == 200 and len(listed.json()) == 1

    detail = client.get(f"/api/resume/{rid}", headers=u["auth"])
    assert detail.status_code == 200
    assert detail.json()["parsed_skills"]

    r = client.delete(f"/api/resume/{rid}", headers=u["auth"])
    assert r.status_code == 204
    assert client.get("/api/resume", headers=u["auth"]).json() == []
