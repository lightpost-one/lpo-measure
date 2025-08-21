import argparse
import os
import sqlite3
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

from lpo_measure.worker import run_case_and_save

from .case import Case
from .db import SQLITE_PATH

N_WORKERS = 3


def add_cases_from_file(filepath: str) -> None:
    """Add cases from a plaintext file where each line is an instruction."""
    file_path = Path(filepath)

    if not file_path.exists():
        print(f"Error: File {filepath} not found")
        return

    with open(file_path, "r") as f:
        instructions = [line.strip() for line in f if line.strip()]

    print(f"Creating {len(instructions)} cases from {filepath}")

    for instruction in instructions:
        case = Case.create(instruction)
        _, created = case.save_to_db()
        if created:
            print(f"Created case: {case.hash} - {instruction}")
        else:
            print(f"Case already exists: {case.hash} - {instruction}")


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


def run_all_cases(script_path: str) -> None:
    """Run measurements against all cases in the database."""
    now = datetime.now()

    cases = Case.load_all_from_db()
    num_cases = len(cases)

    if not cases:
        print("No cases found in the database.")
        return

    print(f"Running {num_cases} cases with {N_WORKERS} workers...")

    benchmark_commit_sha = get_git_commit_sha()

    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        # TODO: Get git commit sha
        cursor.execute(
            "INSERT INTO runs (timestamp, clay_commit_sha, benchmark_commit_sha) VALUES (?, ?, ?)",
            (now.isoformat(), "DEV", benchmark_commit_sha),
        )
        conn.commit()
        run_id = cursor.lastrowid
        assert run_id is not None, "Failed to create run entry"

    with ProcessPoolExecutor(max_workers=N_WORKERS) as executor:
        futures = []
        for case in cases:
            if case.id is None:
                raise TypeError(f"Case {case.hash} has no id.")
            futures.append(executor.submit(run_case_and_save, case.id, run_id, script_path))

        for future in tqdm(as_completed(futures), total=num_cases):
            future.result()

    print("Measurement run complete")


if __name__ == "__main__":
    load_dotenv()
    print(f"{os.getenv('CLAY_CLI_PATH')}")
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

    args = parser.parse_args()

    if args.mode == "add":
        add_cases_from_file(args.file)
    elif args.mode == "run":
        if not args.script:
            raise ValueError("Path to script file not provided and CLAY_CLI_PATH not set.")
        run_all_cases(args.script)
    else:
        raise Exception("Unreachable code.")
