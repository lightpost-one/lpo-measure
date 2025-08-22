from dataclasses import dataclass
from datetime import datetime


@dataclass
class BenchmarkRun:
    """Dataclass to hold all parameters for a benchmark run."""

    script_path: str
    clay_commit_sha: str
    clay_commit_message: str
    model: str
    timestamp: datetime
    benchmark_commit_sha: str
    id: int | None = None
