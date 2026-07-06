import logging
from datetime import datetime
from functools import wraps
from typing import Callable

import bcrypt
from nicegui import app, ui

from core.db import get_db, get_master_db


logger = logging.getLogger(__name__)
DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_ADMIN_PASSWORD = "admin2026"
DEFAULT_TENANT_ID = "default"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        logger.exception("Invalid password hash encountered")
        return False


def ensure_default_admin() -> None:
    """Create a bootstrap admin so Phase 1 can be tested without a user console."""
    conn = None
    try:
        conn = get_master_db()
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count:
            return

        conn.execute(
            """
            INSERT INTO users (email, password_hash, tenant_id, is_active, created_at)
            VALUES (?, ?, ?, 1, ?)
            """,
            (
                DEFAULT_ADMIN_EMAIL,
                hash_password(DEFAULT_ADMIN_PASSWORD),
                DEFAULT_TENANT_ID,
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        get_db(DEFAULT_TENANT_ID).close()
        logger.info("Created default SaaS admin user for tenant '%s'", DEFAULT_TENANT_ID)
    except Exception:
        logger.exception("Failed to create default admin user")
        raise
    finally:
        if conn:
            conn.close()


def authenticate(email: str, password: str) -> dict | None:
    conn = None
    try:
        conn = get_master_db()
        row = conn.execute(
            """
            SELECT id, email, password_hash, tenant_id, is_active
            FROM users
            WHERE lower(email) = lower(?)
            """,
            ((email or "").strip(),),
        ).fetchone()

        if not row or not row["is_active"]:
            return None
        if not verify_password(password or "", row["password_hash"]):
            return None

        get_db(row["tenant_id"]).close()
        return {"email": row["email"], "tenant_id": row["tenant_id"]}
    except Exception:
        logger.exception("Authentication failed due to an internal error")
        return None
    finally:
        if conn:
            conn.close()


def login_user(email: str, tenant_id: str) -> None:
    app.storage.user.update(
        {
            "authenticated": True,
            "tenant_id": tenant_id,
            "email": email,
        }
    )


def logout_user() -> None:
    app.storage.user.clear()
    app.storage.user["authenticated"] = False


def is_authenticated() -> bool:
    return bool(app.storage.user.get("authenticated") and app.storage.user.get("tenant_id"))


def auth_guard() -> bool:
    if is_authenticated():
        return True
    app.storage.user["authenticated"] = False
    ui.navigate.to("/login")
    return False


def require_auth(page_func: Callable) -> Callable:
    @wraps(page_func)
    def wrapper(*args, **kwargs):
        if not auth_guard():
            return
        return page_func(*args, **kwargs)

    return wrapper
