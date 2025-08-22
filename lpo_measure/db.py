import os
import sqlite3
from pathlib import Path

# repo root
_PROD_SQLITE_PATH = Path(__file__).parent.parent / "prod-measurements.db"
_DEV_SQLITE_PATH = Path(__file__).parent.parent / "dev-measurements.db"


def get_db_path() -> Path:
    if os.environ.get("CI"):
        return _PROD_SQLITE_PATH
    return _DEV_SQLITE_PATH


SQLITE_PATH = get_db_path()

SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(SQLITE_PATH) as conn:
    cursor = conn.cursor()

    # Cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT NOT NULL UNIQUE,
        instruction TEXT NOT NULL,
        initial_state TEXT NOT NULL
    )
    """)

    # Runs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        clay_commit_sha TEXT NOT NULL,
        clay_commit_message TEXT NOT NULL,
        benchmark_commit_sha TEXT NOT NULL,
        model TEXT NOT NULL
    )
    """)

    # Measurements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        case_id INTEGER NOT NULL,
        final_state TEXT NOT NULL,
        score INTEGER NOT NULL,
        reason TEXT NOT NULL,
        clay_runtime_seconds REAL NOT NULL,
        judge_runtime_seconds REAL NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (id),
        FOREIGN KEY (case_id) REFERENCES cases (id)
    )
    """)

    conn.commit()
