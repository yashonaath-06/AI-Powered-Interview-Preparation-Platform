def test_signup_returns_token_and_user(client):
    r = client.post("/api/auth/signup", json={
        "email": "alice@example.com",
        "full_name": "Alice",
        "password": "supersecret123",
    })
    assert r.status_code == 201
    data = r.json()
    assert data["access_token"]
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["role"] == "user"


def test_signup_duplicate_email_409(client, make_user):
    make_user("dup@example.com")
    r = client.post("/api/auth/signup", json={
        "email": "dup@example.com",
        "full_name": "Dup",
        "password": "supersecret123",
    })
    assert r.status_code == 409


def test_login_success_and_failure(client, make_user):
    u = make_user("bob@example.com", password="bobpass1234")

    ok = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "bobpass1234"})
    assert ok.status_code == 200
    assert ok.json()["user"]["email"] == "bob@example.com"

    bad = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "wrong"})
    assert bad.status_code == 401


def test_me_endpoint(client, make_user):
    u = make_user("c@example.com", full_name="Charlie")
    r = client.get("/api/auth/me", headers=u["auth"])
    assert r.status_code == 200
    assert r.json()["full_name"] == "Charlie"


def test_protected_endpoint_requires_token(client):
    r = client.get("/api/analytics/summary")
    assert r.status_code == 401


def test_admin_endpoint_requires_admin_role(client, make_user):
    u = make_user("normie@example.com")
    r = client.get("/api/admin/stats", headers=u["auth"])
    assert r.status_code == 403


def test_admin_emails_env_auto_promotes(client, monkeypatch):
    """Verifying the ADMIN_EMAILS auto-promotion path."""
    # NOTE: conftest sets ADMIN_EMAILS="" → user role; we re-test signup logic
    # at the service level here to avoid reload gymnastics.
    from app.services import auth_service
    from app.database import SessionLocal
    from app.schemas.auth import SignupRequest
    from app.config import settings

    object.__setattr__(settings, "admin_emails", "ceo@example.com")

    with SessionLocal() as db:
        user, token = auth_service.signup(db, SignupRequest(
            email="ceo@example.com",
            full_name="The CEO",
            password="ceopassword123",
        ))
    assert user.role == "admin"
