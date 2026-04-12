"""
QualityPulse — Database Layer
Handles SQLite connection, schema initialization, and all query helpers.
"""

import sqlite3
from pathlib import Path

# Always resolve quality.db relative to this file's location
DB_PATH = Path(__file__).parent.parent / "quality.db"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory set to Row."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS defects (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            date            TEXT    NOT NULL,
            shift           TEXT    CHECK(shift IN ('A','B','C')),
            defect_type     TEXT    NOT NULL,
            quantity        INTEGER NOT NULL,
            total_produced  INTEGER NOT NULL,
            line            TEXT    NOT NULL,
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
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# DEFECTS
# ─────────────────────────────────────────────

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


def insert_defect(date: str, shift: str, defect_type: str, quantity: int,
                  total_produced: int, line: str, notes: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO defects (date, shift, defect_type, quantity, total_produced, line, notes) VALUES (?,?,?,?,?,?,?)",
        (date, shift, defect_type, quantity, total_produced, line, notes)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# MEASUREMENTS
# ─────────────────────────────────────────────

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


def get_measurement_points() -> list[str]:
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT measurement_point FROM measurements ORDER BY measurement_point").fetchall()
    conn.close()
    return [r[0] for r in rows]


def insert_measurement(timestamp: str, line: str, measurement_point: str,
                        value: float, nominal: float, tolerance_upper: float, tolerance_lower: float):
    conn = get_connection()
    conn.execute(
        "INSERT INTO measurements (timestamp, line, measurement_point, value, nominal, tolerance_upper, tolerance_lower) VALUES (?,?,?,?,?,?,?)",
        (timestamp, line, measurement_point, value, nominal, tolerance_upper, tolerance_lower)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# CAPA
# ─────────────────────────────────────────────

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


def insert_capa(created_date, title, description, root_cause, corrective_action,
                owner, due_date, criticality, status="Open", closed_date=None):
    conn = get_connection()
    conn.execute(
        """INSERT INTO capa
           (created_date, title, description, root_cause, corrective_action,
            owner, due_date, criticality, status, closed_date)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (created_date, title, description, root_cause, corrective_action,
         owner, due_date, criticality, status, closed_date)
    )
    conn.commit()
    conn.close()


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

def get_all_fmea() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, process_step, failure_mode, failure_effect, severity, occurrence, detection, rpn, "
        "current_controls, recommended_action, responsible, status FROM fmea ORDER BY rpn DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


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


def get_lines() -> list[str]:
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT line FROM defects ORDER BY line").fetchall()
    conn.close()
    return [r[0] for r in rows]
