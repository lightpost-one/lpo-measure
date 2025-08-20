import sqlite3
from pathlib import Path

# repo root
SQLITE_PATH = Path(__file__).parent.parent / "prod-measurements.db"

SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(SQLITE_PATH) as conn:
    cursor = conn.cursor()

    # Cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT NOT NULL UNIQUE,
        instruction TEXT NOT NULL,
        initial_state TEXT
    )
    """)

    # Runs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        clay_commit_sha TEXT,
        benchmark_commit_sha TEXT
    )
    """)

    # Measurements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        case_id INTEGER NOT NULL,
        final_state TEXT,
        score INTEGER NOT NULL,
        reason TEXT,
        clay_runtime_seconds REAL,
        judge_runtime_seconds REAL,
        FOREIGN KEY (run_id) REFERENCES runs (id),
        FOREIGN KEY (case_id) REFERENCES cases (id)
    )
    """)

    conn.commit()
