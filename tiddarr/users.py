"""User accounts and login sessions for the web UI.

Accounts live in the database; a login sets an opaque session token as an
HttpOnly cookie. Admins can create and manage other accounts. The Subsonic
API (/rest/) keeps its own credentials.
"""

import secrets
import time
from functools import wraps

from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import config, db

COOKIE = "tiddarr_session"
SESSION_DAYS = 30
MIN_PASSWORD = 6

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires REAL NOT NULL
);
"""


_DUMMY_HASH = generate_password_hash("dummy")


class UserError(ValueError):
    pass


def init():
    db.conn().executescript(SCHEMA)
    db.run("DELETE FROM sessions WHERE expires < ?", (time.time(),))
    # the old basic-auth credentials become the first admin
    if config.USERNAME and config.PASSWORD and not count():
        create(config.USERNAME, config.PASSWORD, admin=True)


def count() -> int:
    return db.one("SELECT COUNT(*) AS n FROM users")["n"]


def public(u) -> dict:
    return {"id": u["id"], "username": u["username"], "is_admin": bool(u["is_admin"]), "created_at": u["created_at"]}


def all_users() -> list[dict]:
    return [public(u) for u in db.q("SELECT * FROM users ORDER BY username COLLATE NOCASE")]


def get(user_id: int):
    return db.one("SELECT * FROM users WHERE id=?", (user_id,))


def _check_name(username: str) -> str:
    username = (username or "").strip()
    if not username or len(username) > 64:
        raise UserError("invalid_username")
    return username


def _check_password(password: str) -> str:
    if len(password or "") < MIN_PASSWORD:
        raise UserError("password_too_short")
    return password


def _name_taken(username: str, except_id: int | None = None) -> bool:
    r = db.one("SELECT id FROM users WHERE username=?", (username,))
    return bool(r) and r["id"] != except_id


def create(username: str, password: str, admin: bool = False) -> dict:
    username = _check_name(username)
    if _name_taken(username):
        raise UserError("username_taken")
    db.run(
        "INSERT INTO users(username, password_hash, is_admin) VALUES (?, ?, ?)",
        (username, generate_password_hash(_check_password(password)), int(admin)),
    )
    return public(db.one("SELECT * FROM users WHERE username=?", (username,)))


def _admins(except_id: int | None = None) -> int:
    return db.one("SELECT COUNT(*) AS n FROM users WHERE is_admin=1 AND id<>?", (except_id or 0,))["n"]


def update(user_id: int, username: str | None = None, password: str | None = None,
           admin: bool | None = None, keep_session: str | None = None) -> dict:
    """Change an account. A new password logs out all other sessions of that user."""
    u = get(user_id)
    if not u:
        raise UserError("not_found")
    if username is not None:
        username = _check_name(username)
        if _name_taken(username, user_id):
            raise UserError("username_taken")
        db.run("UPDATE users SET username=? WHERE id=?", (username, user_id))
    if admin is not None:
        if not admin and u["is_admin"] and not _admins(user_id):
            raise UserError("last_admin")
        db.run("UPDATE users SET is_admin=? WHERE id=?", (int(admin), user_id))
    if password:
        db.run("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(_check_password(password)), user_id))
        db.run("DELETE FROM sessions WHERE user_id=? AND token<>?", (user_id, keep_session or ""))
    return public(get(user_id))


def delete(user_id: int):
    u = get(user_id)
    if not u:
        raise UserError("not_found")
    if u["is_admin"] and not _admins(user_id):
        raise UserError("last_admin")
    db.run("DELETE FROM users WHERE id=?", (user_id,))


def check_password(u, password: str) -> bool:
    return bool(u) and check_password_hash(u["password_hash"], password or "")


def authenticate(username: str, password: str):
    u = db.one("SELECT * FROM users WHERE username=?", ((username or "").strip(),))
    if check_password(u, password):
        return u
    if not u:  # same work for unknown users, so timing doesn't reveal which names exist
        check_password_hash(_DUMMY_HASH, password or "")
    return None


def new_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    db.run("INSERT INTO sessions(token, user_id, expires) VALUES (?, ?, ?)", (token, user_id, time.time() + SESSION_DAYS * 86400))
    return token


def end_session(token: str):
    db.run("DELETE FROM sessions WHERE token=?", (token or "",))


def from_request():
    """The logged-in user of this request, or None."""
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    r = db.one(
        "SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND s.expires>?",
        (token, time.time()),
    )
    return r


def set_cookie(resp, token: str):
    resp.set_cookie(COOKIE, token, max_age=SESSION_DAYS * 86400, httponly=True, samesite="Lax",
                    secure=request.is_secure or request.headers.get("X-Forwarded-Proto") == "https")
    return resp


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not g.get("user") or not g.user["is_admin"]:
            return jsonify(error="admin_only"), 403
        return fn(*args, **kwargs)

    return wrapper
