import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Case:
    """Represents a test case with instruction and metadata."""

    hash: str
    date_created: str
    instruction: str

    @classmethod
    def create(cls, instruction: str) -> "Case":
        """Create a new case with hash from instruction and current timestamp."""
        instruction_hash = hashlib.sha256(instruction.encode()).hexdigest()[:16]
        return cls(hash=instruction_hash, date_created=datetime.now().isoformat(), instruction=instruction)

    def to_dict(self) -> dict[str, Any]:
        """Convert case to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert case to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Case":
        """Create case from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "Case":
        """Create case from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save_to_file(self, cases_dir: Path) -> Path:
        """Save case to JSON file in cases directory."""
        cases_dir.mkdir(exist_ok=True)
        filename = f"{self.hash}.json"
        filepath = cases_dir / filename
        with open(filepath, "w") as f:
            f.write(self.to_json())
        return filepath

    @classmethod
    def load_from_file(cls, filepath: Path) -> "Case":
        """Load case from JSON file."""
        with open(filepath, "r") as f:
            return cls.from_json(f.read())
