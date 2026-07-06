import functools
import logging
import sqlite3

from nicegui import app

from core.auth import DEFAULT_TENANT_ID
from core.db import get_db, get_tenant_db_path

logger = logging.getLogger(__name__)
DB_PATH = get_tenant_db_path(DEFAULT_TENANT_ID)


def current_tenant_id() -> str:
    try:
        return app.storage.user.get("tenant_id") or DEFAULT_TENANT_ID
    except RuntimeError:
        return DEFAULT_TENANT_ID


def db_operation(default=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.exception("Database operation failed: %s", func.__name__)
                if isinstance(default, list):
                    return []
                return default
        return wrapper
    return decorator


def get_connection(tenant_id: str = None) -> sqlite3.Connection:
    """Return a tenant-scoped SQLite connection."""
    try:
        return get_db(tenant_id or current_tenant_id())
    except Exception:
        logger.exception("Failed to create tenant database connection")
        raise


@db_operation()
def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
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
    """)
    conn.commit()
    conn.close()
    migrate_db()


@db_operation()
def migrate_db():
    """Apply schema updates (alter table) if columns are missing."""
    import re
    conn = get_connection()
    cur = conn.cursor()

    # Check for missing columns in defects
    cur.execute("PRAGMA table_info(defects)")
    cols = [r["name"] for r in cur.fetchall()]

    if "operator" not in cols:
        cur.execute("ALTER TABLE defects ADD COLUMN operator TEXT")
    if "photo_path" not in cols:
        cur.execute("ALTER TABLE defects ADD COLUMN photo_path TEXT")

    # Constraint Migration: Re-create defects table if it has the old CHECK constraint
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='defects'")
    sql = cur.fetchone()[0]
    if "CHECK(shift IN ('A','B','C'))" in sql or "CHECK (shift IN ('A','B','C'))" in sql:
        print("Migrating 'defects' table to remove restrictive shift constraint...")
        cur.execute("ALTER TABLE defects RENAME TO defects_old")
        cur.execute("""
            CREATE TABLE defects (
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
            )
        """)
        cur.execute("""
            INSERT INTO defects (id, date, shift, operator, defect_type, quantity, total_produced, line, photo_path, notes)
            SELECT id, date, shift, operator, defect_type, quantity, total_produced, line, photo_path, notes FROM defects_old
        """)
        cur.execute("DROP TABLE defects_old")
        print("Migration complete.")

    # Data Migration: Extract operator and photo from notes if possible
    rows = cur.execute("SELECT id, notes FROM defects WHERE (operator IS NULL OR photo_path IS NULL) AND notes IS NOT NULL").fetchall()
    for row in rows:
        rid, notes = row["id"], row["notes"]
        if not notes: continue

        op_match = re.search(r"\[Operatör:\s*([^\]]+)\]", notes)
        ph_match = re.search(r"\[PHOTO:\s*([^\]]+)\]", notes)

        updates = []
        params = []
        if op_match:
            updates.append("operator = ?")
            params.append(op_match.group(1).strip())
        if ph_match:
            updates.append("photo_path = ?")
            params.append(ph_match.group(1).strip())

        if updates:
            params.append(rid)
            cur.execute(f"UPDATE defects SET {', '.join(updates)} WHERE id = ?", params)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# DEFECTS
# ─────────────────────────────────────────────

@db_operation(default=[])
def get_defects(start_date: str = None, end_date: str = None, line: str = None) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM defects WHERE 1=1"
    params = []
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if line and line != "Tümü":
        query += " AND line = ?"
        params.append(line)
    query += " ORDER BY date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@db_operation()
def insert_defect(date: str, shift: str, defect_type: str, quantity: int,
                  total_produced: int, line: str, operator: str = None, 
                  photo_path: str = None, notes: str = ""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO defects 
           (date, shift, operator, defect_type, quantity, total_produced, line, photo_path, notes) 
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (date, shift, operator, defect_type, quantity, total_produced, line, photo_path, notes)
    )
    last_id = cur.lastrowid
    log_action(operator or "System", "CREATE", "defects", last_id, f"Entry: {defect_type} ({quantity}) on {line}", conn=conn)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# AUDIT LOGS
# ─────────────────────────────────────────────

@db_operation()
def log_action(user: str, action: str, table_affected: str, record_id: int = None, details: str = "", conn = None):
    """Record an action in the system audit log."""
    from datetime import datetime
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True
    conn.execute(
        "INSERT INTO audit_logs (timestamp, user, action, table_affected, record_id, details) VALUES (?,?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, action, table_affected, record_id, details)
    )
    if should_close:
        conn.commit()
        conn.close()

@db_operation(default=[])
def get_audit_logs(limit: int = 200) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────
# MEASUREMENTS
# ─────────────────────────────────────────────

@db_operation(default=[])
def get_measurements(measurement_point: str = None, limit: int = 100) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM measurements"
    params = []
    if measurement_point and measurement_point != "Tümü":
        query += " WHERE measurement_point = ?"
        params.append(measurement_point)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@db_operation(default=[])
def get_measurement_points() -> list[str]:
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT measurement_point FROM measurements ORDER BY measurement_point").fetchall()
    conn.close()
    return [r[0] for r in rows]


@db_operation()
def insert_measurement(timestamp: str, line: str, measurement_point: str,
                        value: float, nominal: float, tolerance_upper: float, tolerance_lower: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO measurements (timestamp, line, measurement_point, value, nominal, tolerance_upper, tolerance_lower) VALUES (?,?,?,?,?,?,?)",
        (timestamp, line, measurement_point, value, nominal, tolerance_upper, tolerance_lower)
    )
    last_id = cur.lastrowid
    log_action("System", "CREATE", "measurements", last_id, f"Inspection: {measurement_point} -> {value}", conn=conn)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# CAPA
# ─────────────────────────────────────────────

@db_operation(default=[])
def get_all_capa(status_filter: list = None, criticality_filter: list = None, owner_search: str = "") -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM capa WHERE 1=1"
    params = []
    if status_filter:
        placeholders = ",".join("?" * len(status_filter))
        query += f" AND status IN ({placeholders})"
        params.extend(status_filter)
    if criticality_filter:
        placeholders = ",".join("?" * len(criticality_filter))
        query += f" AND criticality IN ({placeholders})"
        params.extend(criticality_filter)
    if owner_search:
        query += " AND owner LIKE ?"
        params.append(f"%{owner_search}%")
    query += " ORDER BY created_date DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@db_operation()
def insert_capa(created_date, title, description, root_cause, corrective_action,
                owner, due_date, criticality, status="Open", closed_date=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO capa
           (created_date, title, description, root_cause, corrective_action,
            owner, due_date, criticality, status, closed_date)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (created_date, title, description, root_cause, corrective_action,
         owner, due_date, criticality, status, closed_date)
    )
    last_id = cur.lastrowid
    log_action(owner, "CREATE", "capa", last_id, f"Action: {title}", conn=conn)
    conn.commit()
    conn.close()


@db_operation()
def update_capa_status(capa_id: int, new_status: str, closed_date: str = None):
    conn = get_connection()
    conn.execute(
        "UPDATE capa SET status=?, closed_date=? WHERE id=?",
        (new_status, closed_date, capa_id)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# FMEA
# ─────────────────────────────────────────────

@db_operation(default=[])
def get_all_fmea() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, process_step, failure_mode, failure_effect, severity, occurrence, detection, rpn, "
        "current_controls, recommended_action, responsible, status FROM fmea ORDER BY rpn DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@db_operation()
def insert_fmea(process_step, failure_mode, failure_effect, severity, occurrence, detection,
                current_controls, recommended_action, responsible, status="Open"):
    conn = get_connection()
    conn.execute(
        """INSERT INTO fmea
           (process_step, failure_mode, failure_effect, severity, occurrence, detection,
            current_controls, recommended_action, responsible, status)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (process_step, failure_mode, failure_effect, severity, occurrence, detection,
         current_controls, recommended_action, responsible, status)
    )
    conn.commit()
    conn.close()


@db_operation()
def update_fmea(fmea_id: int, **kwargs):
    conn = get_connection()
    allowed = {"process_step", "failure_mode", "failure_effect", "severity", "occurrence",
                "detection", "current_controls", "recommended_action", "responsible", "status"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [fmea_id]
    conn.execute(f"UPDATE fmea SET {set_clause} WHERE id=?", values)
    conn.commit()
    conn.close()


@db_operation(default=[])
def get_lines() -> list[str]:
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT line FROM defects ORDER BY line").fetchall()
    conn.close()
    return [r[0] for r in rows]
