import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import orjson

from .db import SQLITE_PATH


@dataclass
class Case:
    """A Case is a user instruction on top of an initial state."""

    hash: str
    instruction: str
    initial_state: dict[str, Any]
    id: int | None = None

    @classmethod
    def create(cls, instruction: str, initial_state: dict[str, Any] | None = None) -> "Case":
        """Create a new case with hash from instruction and current timestamp."""
        if initial_state is None:
            initial_state = {"nodes": [], "edges": []}

        to_hash = instruction.encode() + orjson.dumps(initial_state, option=orjson.OPT_SORT_KEYS)

        instruction_hash = hashlib.sha256(to_hash).hexdigest()[:16]
        return cls(
            hash=instruction_hash,
            instruction=instruction,
            initial_state=initial_state,
        )

    def save_to_db(self) -> tuple[int, bool]:
        """Save case to the database if it doesn't already exist."""
        with sqlite3.connect(SQLITE_PATH) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO cases (hash, instruction, initial_state)
                    VALUES (?, ?, ?)
                    """,
                    (
                        self.hash,
                        self.instruction,
                        orjson.dumps(self.initial_state).decode(),
                    ),
                )
                conn.commit()
                self.id = cursor.lastrowid
                if self.id is None:
                    raise TypeError("Failed to get last row id.")
                return self.id, True
            except sqlite3.IntegrityError:
                # Case with this hash already exists
                cursor.execute("SELECT id FROM cases WHERE hash = ?", (self.hash,))
                row = cursor.fetchone()
                if row is None:
                    raise TypeError("Failed to fetch existing case.")
                self.id = row[0]
                if self.id is None:
                    raise TypeError("Failed to get last row id.")
                return self.id, False

    @classmethod
    def load_from_db(cls, case_id: int) -> "Case":
        """Load a case from the database by its ID."""
        with sqlite3.connect(SQLITE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, hash, instruction, initial_state FROM cases WHERE id = ?", (case_id,))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row[0],
                    hash=row[1],
                    instruction=row[2],
                    initial_state=orjson.loads(row[3]),
                )
            raise ValueError(f"Case with id {case_id} not found")

    @classmethod
    def load_all_from_db(cls) -> list["Case"]:
        """Load all cases from the database."""
        with sqlite3.connect(SQLITE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, hash, instruction, initial_state FROM cases")
            cases = []
            for row in cursor.fetchall():
                cases.append(
                    cls(
                        id=row[0],
                        hash=row[1],
                        instruction=row[2],
                        initial_state=orjson.loads(row[3]),
                    )
                )
            return cases


@dataclass
class CaseResult:
    """A CaseResult is a score and reason behind the score."""

    score: int
    reason: str


@dataclass
class CaseMeasurement:
    """Everything about a full case measurement."""

    case: Case
    final_state: dict[str, Any] | None
    result: CaseResult
    clay_runtime: float
    judge_runtime: float
    date_measured: str

    @classmethod
    def create(
        cls,
        case: Case,
        final_state: dict[str, Any] | None,
        result: CaseResult,
        clay_runtime: float,
        judge_runtime: float,
    ) -> "CaseMeasurement":
        """Create a new case result with current timestamp."""
        return cls(
            case=case,
            final_state=final_state,
            result=result,
            clay_runtime=clay_runtime,
            judge_runtime=judge_runtime,
            date_measured=datetime.now().isoformat(),
        )

    def save_to_db(self, run_id: int):
        """Save case measurement to the database."""
        with sqlite3.connect(SQLITE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO measurements (run_id, case_id, final_state, score, reason, clay_runtime_seconds, judge_runtime_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    self.case.id,
                    orjson.dumps(self.final_state).decode() if self.final_state else None,
                    self.result.score,
                    self.result.reason,
                    self.clay_runtime,
                    self.judge_runtime,
                ),
            )
            conn.commit()
