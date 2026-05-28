def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "AI Interview Preparation Platform" in r.json()["name"]


def test_openapi_includes_main_routes(client):
    paths = client.get("/openapi.json").json()["paths"]
    for p in [
        "/api/health", "/api/auth/signup", "/api/auth/login", "/api/auth/me",
        "/api/interviews", "/api/interviews/{session_id}/answer",
        "/api/interviews/{session_id}/answer/audio",
        "/api/interviews/{session_id}/vision/frame",
        "/api/questions", "/api/questions/meta",
        "/api/resume/analyze",
        "/api/analytics/summary", "/api/analytics/trend",
        "/api/admin/users", "/api/admin/stats",
    ]:
        assert p in paths, f"Missing OpenAPI path: {p}"
