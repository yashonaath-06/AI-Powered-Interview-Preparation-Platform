"""
Shared pytest fixtures.

Each test gets a fresh in-memory SQLite database via dependency_overrides.
Routers see the fresh DB; settings stay singletons.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app


@pytest.fixture(scope="function")
def client(monkeypatch, tmp_path):
    """Fresh app + DB per test using dependency_overrides."""
    # Patch settings (some routes read directly)
    monkeypatch.setenv("ADMIN_EMAILS", "")

    # Build a per-test SQLite engine
    db_url = f"sqlite:///{tmp_path}/test.db"
    test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    # IMPORTANT: import all model modules so they register on Base.metadata
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=test_engine)

    # Seed the question bank for tests that need it
    import json
    from pathlib import Path
    from app.models.question import Question

    bank_path = Path("app/data/question_bank.json")
    if bank_path.exists():
        with TestSession() as db:
            with bank_path.open() as f:
                data = json.load(f)
            for item in data["questions"]:
                db.add(Question(
                    text=item["text"],
                    category=item["category"],
                    difficulty=item.get("difficulty", "medium"),
                    company=item.get("company"),
                    role=item.get("role"),
                    expected_keywords=(
                        json.dumps(item["expected_keywords"])
                        if item.get("expected_keywords") else None
                    ),
                    sample_answer=item.get("sample_answer"),
                ))
            db.commit()

    # Override get_db
    def _override_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_db

    # Manually trigger startup since we are not using TestClient as ctx manager
    # for the lifespan (we don't want init_db to run against a different DB).
    with TestClient(app) as c:
        # Replace get_db AFTER lifespan ran (lifespan also calls get_db indirectly via seeder,
        # but seeder uses SessionLocal, not get_db).
        c.app.dependency_overrides[get_db] = _override_db
        # Provide the override engine to the seeder by patching SessionLocal
        # for tests that exercise admin promote/demote which uses raw SessionLocal
        import app.database as _db_mod
        _orig_session_local = _db_mod.SessionLocal
        _db_mod.SessionLocal = TestSession  # type: ignore
        try:
            yield c
        finally:
            _db_mod.SessionLocal = _orig_session_local
            app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def make_user(client):
    counter = {"i": 0}

    def _make(email: str | None = None, password: str = "password1234", full_name: str = "Test User"):
        counter["i"] += 1
        e = email or f"user{counter['i']}@example.com"
        r = client.post("/api/auth/signup", json={
            "email": e, "password": password, "full_name": full_name,
        })
        assert r.status_code == 201, r.text
        token = r.json()["access_token"]
        user = r.json()["user"]
        return {
            "email": e,
            "user": user,
            "auth": {"Authorization": f"Bearer {token}"},
        }

    return _make
