"""
Tiny CLI — bootstrap and admin utilities.

Usage:
    python -m app.cli make-admin   you@example.com
    python -m app.cli make-user    you@example.com
    python -m app.cli list-users
    python -m app.cli reset-password user@example.com newSecret123

Run from inside the `backend/` directory with the venv activated.
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal, init_db
from app.models.user import User


def _resolve(db, email: str) -> User:
    u = db.scalar(select(User).where(User.email == email))
    if u is None:
        sys.exit(f"❌ no user found with email={email}")
    return u


def cmd_make_admin(email: str):
    init_db()
    with SessionLocal() as db:
        u = _resolve(db, email)
        u.role = "admin"
        db.commit()
        print(f"✅ {u.email} is now an admin.")


def cmd_make_user(email: str):
    init_db()
    with SessionLocal() as db:
        u = _resolve(db, email)
        u.role = "user"
        db.commit()
        print(f"✅ {u.email} is now a normal user.")


def cmd_list_users():
    init_db()
    with SessionLocal() as db:
        users = list(db.scalars(select(User).order_by(User.created_at)).all())
        if not users:
            print("(no users)")
            return
        for u in users:
            print(f"  #{u.id:>3}  {u.role:<5}  {u.email:<32}  {u.full_name}")


def cmd_reset_password(email: str, new_password: str):
    if len(new_password) < 8:
        sys.exit("❌ password must be at least 8 characters.")
    init_db()
    with SessionLocal() as db:
        u = _resolve(db, email)
        u.hashed_password = hash_password(new_password)
        db.commit()
        print(f"✅ password updated for {u.email}.")


def main(argv: list[str] | None = None):
    p = argparse.ArgumentParser(prog="app.cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("make-admin"); s.add_argument("email")
    s = sub.add_parser("make-user");  s.add_argument("email")
    sub.add_parser("list-users")
    s = sub.add_parser("reset-password"); s.add_argument("email"); s.add_argument("new_password")

    args = p.parse_args(argv)
    if args.cmd == "make-admin":      cmd_make_admin(args.email)
    elif args.cmd == "make-user":     cmd_make_user(args.email)
    elif args.cmd == "list-users":    cmd_list_users()
    elif args.cmd == "reset-password": cmd_reset_password(args.email, args.new_password)


if __name__ == "__main__":
    main()
