import os
import logging
import re
import sqlite3
from pathlib import Path


logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent
DATA_DIR = Path(os.environ["QP_DATA_DIR"]) if "QP_DATA_DIR" in os.environ else PROJECT_ROOT / "data"
TENANT_DIR = DATA_DIR / "tenants"
MASTER_DB_PATH = DATA_DIR / "master.db"


TENANT_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS defects (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        date            TEXT    NOT NULL,
        shift           TEXT    NOT NULL,
        operator        TEXT,
        defect_type     TEXT    NOT NULL,
        quantity        INTEGER NOT NULL,
        total_produced  INTEGER NOT NULL,
        line            TEXT    NOT NULL,
        photo_path      TEXT,
        notes           TEXT
    );

    CREATE TABLE IF NOT EXISTS measurements (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp           TEXT    NOT NULL,
        line                TEXT    NOT NULL,
        measurement_point   TEXT    NOT NULL,
        value               REAL    NOT NULL,
        nominal             REAL    NOT NULL,
        tolerance_upper     REAL    NOT NULL,
        tolerance_lower     REAL    NOT NULL
    );

    CREATE TABLE IF NOT EXISTS capa (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        created_date        TEXT    NOT NULL,
        title               TEXT    NOT NULL,
        description         TEXT    NOT NULL,
        root_cause          TEXT,
        corrective_action   TEXT,
        owner               TEXT    NOT NULL,
        due_date            TEXT    NOT NULL,
        criticality         TEXT    CHECK(criticality IN ('Critical','Major','Minor')),
        status              TEXT    CHECK(status IN ('Open','In Progress','Closed')) DEFAULT 'Open',
        closed_date         TEXT
    );

    CREATE TABLE IF NOT EXISTS fmea (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        process_step        TEXT    NOT NULL,
        failure_mode        TEXT    NOT NULL,
        failure_effect      TEXT    NOT NULL,
        severity            INTEGER CHECK(severity BETWEEN 1 AND 10),
        occurrence          INTEGER CHECK(occurrence BETWEEN 1 AND 10),
        detection           INTEGER CHECK(detection BETWEEN 1 AND 10),
        rpn                 INTEGER GENERATED ALWAYS AS (severity * occurrence * detection) VIRTUAL,
        current_controls    TEXT,
        recommended_action  TEXT,
        responsible         TEXT,
        status              TEXT    CHECK(status IN ('Open','In Progress','Closed')) DEFAULT 'Open'
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp       TEXT    NOT NULL,
        user            TEXT    NOT NULL,
        action          TEXT    NOT NULL,
        table_affected  TEXT    NOT NULL,
        record_id       INTEGER,
        details         TEXT
    );
"""


MASTER_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        email           TEXT    NOT NULL UNIQUE,
        password_hash   TEXT    NOT NULL,
        tenant_id       TEXT    NOT NULL,
        is_active       INTEGER NOT NULL DEFAULT 1,
        created_at      TEXT    NOT NULL
    );
"""


def ensure_data_dirs() -> None:
    try:
        TENANT_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.exception("Failed to create SaaS data directories")
        raise


def sanitize_tenant_id(tenant_id: str) -> str:
    tenant = (tenant_id or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9_-]{1,64}", tenant):
        raise ValueError("Invalid tenant_id. Use lowercase letters, numbers, underscores, or hyphens.")
    return tenant


def get_tenant_db_path(tenant_id: str) -> Path:
    ensure_data_dirs()
    return TENANT_DIR / f"{sanitize_tenant_id(tenant_id)}.db"


def _configure_connection(conn: sqlite3.Connection) -> sqlite3.Connection:
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def initialize_tenant_schema(conn: sqlite3.Connection) -> None:
    try:
        conn.executescript(TENANT_SCHEMA_SQL)
        conn.commit()
    except sqlite3.Error:
        logger.exception("Failed to initialize tenant schema")
        raise


def get_db(tenant_id: str) -> sqlite3.Connection:
    """Return a SQLite connection for one isolated tenant database."""
    try:
        db_path = get_tenant_db_path(tenant_id)
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        _configure_connection(conn)
        initialize_tenant_schema(conn)
        return conn
    except (sqlite3.Error, OSError, ValueError):
        logger.exception("Failed to open tenant database for tenant_id=%s", tenant_id)
        raise


def get_master_db() -> sqlite3.Connection:
    try:
        ensure_data_dirs()
        conn = sqlite3.connect(str(MASTER_DB_PATH), check_same_thread=False)
        _configure_connection(conn)
        conn.executescript(MASTER_SCHEMA_SQL)
        conn.commit()
        return conn
    except (sqlite3.Error, OSError):
        logger.exception("Failed to open master database")
        raise
