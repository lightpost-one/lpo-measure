import argparse
import time
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import orjson
from tqdm import tqdm

from lpo_measure.worker import run_case_and_save

from .case import Case

N_WORKERS = 3


def add_cases_from_file(filepath: str) -> None:
    """Add cases from a plaintext file where each line is an instruction."""
    file_path = Path(filepath)
    cases_path = Path("cases")

    if not file_path.exists():
        print(f"Error: File {filepath} not found")
        return

    cases_path.mkdir(exist_ok=True)

    with open(file_path, "r") as f:
        instructions = [line.strip() for line in f if line.strip()]

    print(f"Creating {len(instructions)} cases from {filepath}")

    for instruction in instructions:
        case = Case.create(instruction)
        _, created = case.save_to_file(cases_path)
        if created:
            print(f"Created case: {case.hash} - {instruction}")
        else:
            print(f"Case already exists: {case.hash} - {instruction}")


def run_all_cases() -> None:
    """Run measurements against all cases in the cases folder."""
    cases_path = Path("cases")
    now = datetime.now()
    measurements_dir_name = f"measurements_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
    measurements_path = Path(measurements_dir_name)

    if not cases_path.exists():
        print("No cases directory found")
        return

    case_files = list(cases_path.glob("*.json"))
    num_cases = len(case_files)

    if not case_files:
        print("No cases found")
        return

    measurements_path.mkdir(exist_ok=True)
    print(f"Running {num_cases} cases with {N_WORKERS} workers...")

    total_score = 0
    start_time = time.time()

    with Pool(N_WORKERS) as pool:
        tasks = [(case_file, measurements_path) for case_file in case_files]
        for measurement in tqdm(
            pool.imap(run_case_and_save, tasks),
            total=num_cases,
            desc="Processing cases",
        ):
            total_score += measurement.result.score

    end_time = time.time()
    total_runtime = end_time - start_time
    aggregate_score = total_score / num_cases if num_cases > 0 else 0
    aggregate_score /= 3.0

    report = {
        "total_runtime": total_runtime,
        "aggregate_score": aggregate_score,
        "num_cases": num_cases,
    }

    report_path = measurements_path / "report.json"
    with open(report_path, "wb") as f:
        f.write(orjson.dumps(report, option=orjson.OPT_INDENT_2))

    print(f"Measurement run complete. Report saved to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LPO Measure")
    subparsers = parser.add_subparsers(dest="mode", help="Operation mode")

    # Add cases mode
    add_parser = subparsers.add_parser("add", help="Add cases from file")
    add_parser.add_argument("file", help="Plaintext file with instructions")

    # Run mode
    run_parser = subparsers.add_parser("run", help="Run all cases")

    args = parser.parse_args()

    if args.mode == "add":
        add_cases_from_file(args.file)
    elif args.mode == "run":
        run_all_cases()
    else:
        raise Exception("Unreachable code.")
