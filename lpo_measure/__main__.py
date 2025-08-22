import argparse
import logging
import os
import sqlite3
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

from lpo_measure.run import BenchmarkRun
from lpo_measure.worker import run_case_and_save

from .case import Case
from .db import SQLITE_PATH
from .log import setup_logging

N_WORKERS = 3


def add_cases_from_file(filepath: str) -> None:
    """Add cases from a plaintext file where each line is an instruction."""
    file_path = Path(filepath)

    if not file_path.exists():
        logging.error(f"Error: File {filepath} not found")
        return

    with open(file_path, "r") as f:
        instructions = [line.strip() for line in f if line.strip()]

    logging.info(f"Creating {len(instructions)} cases from {filepath}")

    for instruction in instructions:
        Case.get_or_create(instruction)


def get_git_commit_sha() -> str:
    """Get the current git commit sha, preferring GITHUB_SHA env var."""
    github_sha = os.getenv("GITHUB_SHA")
    if github_sha:
        return github_sha
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def run_all_cases(
    script_path: str,
    clay_commit_sha: str,
    clay_commit_message: str,
    model: str,
) -> None:
    """Run measurements against all cases in the database."""
    run = BenchmarkRun(
        script_path=script_path,
        clay_commit_sha=clay_commit_sha,
        clay_commit_message=clay_commit_message,
        model=model,
        timestamp=datetime.now(),
        benchmark_commit_sha=get_git_commit_sha(),
    )

    cases = Case.load_all_from_db()
    num_cases = len(cases)

    if not cases:
        logging.info("No cases found in the database.")
        return

    logging.info(f"Running {num_cases} cases with {N_WORKERS} workers...")

    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO runs (timestamp, clay_commit_sha, clay_commit_message, benchmark_commit_sha, model) VALUES (?, ?, ?, ?, ?)",
            (
                run.timestamp.isoformat(),
                run.clay_commit_sha,
                run.clay_commit_message,
                run.benchmark_commit_sha,
                run.model,
            ),
        )
        conn.commit()
        run.id = cursor.lastrowid
        assert run.id is not None, "Failed to create run entry"

    with ProcessPoolExecutor(max_workers=N_WORKERS, initializer=setup_logging) as executor:
        futures = []
        for case in cases:
            futures.append(executor.submit(run_case_and_save, case, run))

        for future in tqdm(as_completed(futures), total=num_cases):
            future.result()

    logging.info("Measurement run complete")


if __name__ == "__main__":
    setup_logging()
    load_dotenv()
    parser = argparse.ArgumentParser(description="LPO Measure")
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")

    # Add cases mode
    add_parser = subparsers.add_parser("add", help="Add cases from file")
    add_parser.add_argument("file", help="Plaintext file with instructions")

    # Run mode
    run_parser = subparsers.add_parser("run", help="Run all cases")
    run_parser.add_argument(
        "--script",
        help="Path to the script file",
        default=os.getenv("CLAY_CLI_PATH"),
    )
    run_parser.add_argument(
        "--clay-commit-sha",
        help="Git commit SHA of the clay script",
        default="DEV",
    )
    run_parser.add_argument(
        "--clay-commit-message",
        help="Git commit message of the clay script",
        default="DEV",
    )
    run_parser.add_argument(
        "--model",
        help="Model name to use",
        default="gpt-5-mini",
    )

    args = parser.parse_args()

    if args.mode == "add":
        add_cases_from_file(args.file)
    elif args.mode == "run":
        if not args.script:
            raise ValueError("Path to script file not provided and CLAY_CLI_PATH not set.")
        run_all_cases(
            args.script,
            args.clay_commit_sha,
            args.clay_commit_message,
            args.model,
        )
    else:
        raise Exception("Unreachable code.")
