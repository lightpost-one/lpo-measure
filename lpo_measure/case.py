import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import orjson


@dataclass
class Case:
    """A Case is a user instruction on top of an initial state."""

    hash: str
    date_created: str
    instruction: str
    initial_state: dict[str, Any]

    @classmethod
    def create(cls, instruction: str, initial_state: dict[str, Any] | None = None) -> "Case":
        """Create a new case with hash from instruction and current timestamp."""
        if initial_state is None:
            initial_state = {"nodes": [], "edges": []}

        to_hash = instruction.encode() + orjson.dumps(initial_state, option=orjson.OPT_SORT_KEYS)

        instruction_hash = hashlib.sha256(to_hash).hexdigest()[:16]
        return cls(
            hash=instruction_hash,
            date_created=datetime.now().isoformat(),
            instruction=instruction,
            initial_state=initial_state,
        )

    def save_to_file(self, cases_dir: Path) -> tuple[Path, bool]:
        """Save case to JSON file in cases directory if it doesn't already exist."""
        cases_dir.mkdir(exist_ok=True)
        filename = f"{self.hash}.json"
        filepath = cases_dir / filename

        if not filepath.exists():
            with open(filepath, "wb") as f:
                f.write(orjson.dumps(asdict(self), option=orjson.OPT_INDENT_2))
            return filepath, True

        return filepath, False

    @classmethod
    def load_from_file(cls, filepath: Path) -> "Case":
        """Load case from JSON file."""
        with open(filepath, "rb") as f:
            data = orjson.loads(f.read())
            return cls(**data)


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
    runtime: float
    date_measured: str

    @classmethod
    def create(
        cls,
        case: Case,
        final_state: dict[str, Any] | None,
        result: CaseResult,
        runtime: float,
    ) -> "CaseMeasurement":
        """Create a new case result with current timestamp."""
        return cls(
            case=case,
            final_state=final_state,
            result=result,
            runtime=runtime,
            date_measured=datetime.now().isoformat(),
        )

    def save_to_file(self, measurements_dir: Path) -> Path:
        """Save case result to JSON file in measurements directory."""
        measurements_dir.mkdir(exist_ok=True)
        filename = f"{self.case.hash}.json"
        filepath = measurements_dir / filename
        with open(filepath, "wb") as f:
            f.write(orjson.dumps(asdict(self), option=orjson.OPT_INDENT_2))
        return filepath

    @classmethod
    def load_from_file(cls, filepath: Path) -> "CaseMeasurement":
        """Load case result from JSON file."""
        with open(filepath, "rb") as f:
            data = orjson.loads(f.read())
            return cls(**data)
