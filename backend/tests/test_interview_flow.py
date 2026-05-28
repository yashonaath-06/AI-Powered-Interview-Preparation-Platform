"""End-to-end interview lifecycle test (text answers only)."""


def test_full_interview_lifecycle(client, make_user):
    u = make_user()

    # 1. Question meta is reachable
    r = client.get("/api/questions/meta")
    assert r.status_code == 200
    meta = r.json()
    assert "Google" in meta["companies"]

    # 2. Start a 3-question session
    r = client.post("/api/interviews", headers=u["auth"], json={
        "company": "Google",
        "role": "Software Engineer",
        "interview_type": "mixed",
        "num_questions": 3,
    })
    assert r.status_code == 201
    sid = r.json()["session_id"]
    first_q = r.json()["question"]
    assert first_q["text"]

    # 3. Submit good, weak, good answers
    answers = [
        "Dynamic programming relies on overlapping subproblems and optimal substructure. "
        "We avoid recomputing using memoization or tabulation. Examples: knapsack and Fibonacci.",
        "Um, like, I dont know.",
        "I would design YouTube's recommendation system as candidate generation followed by "
        "ranking, using embeddings and watch history features, evaluated with AB tests.",
    ]
    for ans in answers:
        r = client.post(f"/api/interviews/{sid}/answer",
                        headers=u["auth"],
                        json={"answer_text": ans})
        assert r.status_code == 200
        assert "overall" in r.json()["scores"]

    # 4. 4th answer should 409
    r = client.post(f"/api/interviews/{sid}/answer", headers=u["auth"], json={"answer_text": "extra"})
    assert r.status_code == 409

    # 5. Complete + report
    r = client.post(f"/api/interviews/{sid}/complete", headers=u["auth"])
    assert r.status_code == 200 and r.json()["status"] == "completed"

    r = client.get(f"/api/interviews/{sid}/report", headers=u["auth"])
    rep = r.json()
    assert len(rep["items"]) == 3
    assert rep["session"]["overall_score"] is not None
    assert rep["ai_feedback"]


def test_cross_user_session_access_denied(client, make_user):
    a = make_user("a@x.com")
    r = client.post("/api/interviews", headers=a["auth"], json={"interview_type": "hr", "num_questions": 1})
    sid = r.json()["session_id"]

    b = make_user("b@x.com")
    r = client.get(f"/api/interviews/{sid}", headers=b["auth"])
    assert r.status_code == 404
    r = client.get(f"/api/interviews/{sid}/report", headers=b["auth"])
    assert r.status_code == 404


def test_analytics_reflect_completed_session(client, make_user):
    u = make_user()
    r = client.post("/api/interviews", headers=u["auth"], json={"interview_type": "hr", "num_questions": 1})
    sid = r.json()["session_id"]
    client.post(f"/api/interviews/{sid}/answer", headers=u["auth"], json={"answer_text": "I am a hard worker who loves to learn."})
    client.post(f"/api/interviews/{sid}/complete", headers=u["auth"])

    s = client.get("/api/analytics/summary", headers=u["auth"]).json()
    assert s["completed_sessions"] == 1
    assert s["average_score"] is not None

    t = client.get("/api/analytics/trend", headers=u["auth"]).json()
    assert t["count"] == 1


def test_audio_endpoint_503_without_whisper(client, make_user):
    """Without faster-whisper installed, audio submit returns 503 not crash."""
    import io
    u = make_user()
    r = client.post("/api/interviews", headers=u["auth"], json={"interview_type": "hr", "num_questions": 1})
    sid = r.json()["session_id"]
    fake = io.BytesIO(b"not real audio")
    r = client.post(f"/api/interviews/{sid}/answer/audio",
                    headers=u["auth"],
                    files={"audio": ("x.webm", fake, "audio/webm")})
    # If whisper is installed in this env we get 422 (empty transcript) or 200; otherwise 503.
    assert r.status_code in (200, 422, 503)
