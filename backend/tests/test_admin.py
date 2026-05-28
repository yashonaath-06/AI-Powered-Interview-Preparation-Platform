"""Admin endpoint tests — role gating, CRUD, self-protect."""
import pytest


def _promote_via_db(email: str):
    """Helper: mark a user as admin directly in the DB (bypasses ADMIN_EMAILS)."""
    from sqlalchemy import select
    from app.database import SessionLocal
    from app.models.user import User
    with SessionLocal() as db:
        u = db.scalar(select(User).where(User.email == email))
        u.role = "admin"
        db.commit()


@pytest.fixture
def admin(client, make_user):
    a = make_user("admin@example.com")
    _promote_via_db("admin@example.com")
    # Re-login so the new role is in the JWT (also re-issues for /me)
    r = client.post("/api/auth/login", json={
        "email": "admin@example.com", "password": "password1234",
    })
    return {
        "auth": {"Authorization": f"Bearer {r.json()['access_token']}"},
        "user": r.json()["user"],
    }


def test_non_admin_blocked_from_admin_routes(client, make_user):
    u = make_user()
    for path in ["/api/admin/users", "/api/admin/stats", "/api/admin/sessions"]:
        r = client.get(path, headers=u["auth"])
        assert r.status_code == 403, path


def test_admin_can_list_users(client, admin, make_user):
    make_user("alice@example.com")
    make_user("bob@example.com")
    r = client.get("/api/admin/users", headers=admin["auth"])
    assert r.status_code == 200
    assert r.json()["total"] >= 3


def test_admin_user_search(client, admin, make_user):
    make_user("alice@example.com", full_name="Alice In Wonderland")
    r = client.get("/api/admin/users", headers=admin["auth"], params={"q": "wonderland"})
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["email"] == "alice@example.com"


def test_admin_promote_and_demote(client, admin, make_user):
    target = make_user("normie@example.com")
    target_id = target["user"]["id"]

    r = client.patch(f"/api/admin/users/{target_id}/role",
                     headers=admin["auth"], json={"role": "admin"})
    assert r.status_code == 200 and r.json()["role"] == "admin"

    r = client.patch(f"/api/admin/users/{target_id}/role",
                     headers=admin["auth"], json={"role": "user"})
    assert r.status_code == 200 and r.json()["role"] == "user"


def test_admin_cannot_demote_self(client, admin):
    me_id = admin["user"]["id"]
    r = client.patch(f"/api/admin/users/{me_id}/role",
                     headers=admin["auth"], json={"role": "user"})
    assert r.status_code == 400


def test_admin_question_crud(client, admin):
    # Create
    r = client.post("/api/admin/questions", headers=admin["auth"], json={
        "text": "What is your favourite design pattern?",
        "category": "technical",
        "difficulty": "medium",
        "expected_keywords": ["singleton", "factory", "observer"],
    })
    assert r.status_code == 201
    qid = r.json()["id"]

    # Update
    r = client.patch(f"/api/admin/questions/{qid}",
                     headers=admin["auth"], json={"difficulty": "hard"})
    assert r.status_code == 200 and r.json()["difficulty"] == "hard"

    # Delete
    r = client.delete(f"/api/admin/questions/{qid}", headers=admin["auth"])
    assert r.status_code == 204


def test_admin_stats_shape(client, admin):
    r = client.get("/api/admin/stats", headers=admin["auth"])
    assert r.status_code == 200
    j = r.json()
    for k in ("user_count", "admin_count", "question_count", "session_count",
              "completion_rate_pct", "platform_average_score",
              "top_companies", "newest_users"):
        assert k in j
