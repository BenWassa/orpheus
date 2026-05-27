from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"
_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    schema_sql = _SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)
    conn.commit()


def get_schema_version(conn: sqlite3.Connection) -> int:
    try:
        row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
        return row[0] if row[0] is not None else 0
    except sqlite3.OperationalError:
        return 0


def run_migrations(conn: sqlite3.Connection) -> list[int]:
    current = get_schema_version(conn)
    applied = []

    if not _MIGRATIONS_DIR.exists():
        return applied

    migration_files = sorted(_MIGRATIONS_DIR.glob("*.sql"))
    for mf in migration_files:
        version = int(mf.name.split("_")[0])
        if version <= current:
            continue

        sql = mf.read_text()
        conn.executescript(sql)
        conn.execute(
            "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
            (version, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        applied.append(version)

    return applied


def get_table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    tables = ["plays", "tracks", "audio_features", "lyrics", "track_scores", "artists", "pipeline_runs"]
    counts = {}
    for table in tables:
        try:
            row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            counts[table] = row[0]
        except sqlite3.OperationalError:
            counts[table] = -1
    return counts


def get_last_run(conn: sqlite3.Connection) -> dict | None:
    try:
        row = conn.execute(
            "SELECT run_id, finished_at, output_path FROM pipeline_runs ORDER BY finished_at DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return {"run_id": row["run_id"], "finished_at": row["finished_at"], "output_path": row["output_path"]}
    except sqlite3.OperationalError:
        return None
