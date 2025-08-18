import argparse
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from lpo_measure.clay import run_case

from .case import Case


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
        case_file_path = case.save_to_file(cases_path)
        if case_file_path.exists() and case_file_path.stat().st_size > 0:
            existing_case = Case.load_from_file(case_file_path)
            if existing_case.instruction == instruction:
                print(f"Case already exists: {case.hash} - {instruction}")
            else:
                print(f"Created case: {case.hash} - {instruction}")
        else:
            print(f"Created case: {case.hash} - {instruction}")


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

    if not case_files:
        print("No cases found")
        return

    measurements_path.mkdir(exist_ok=True)
    print(f"Running {len(case_files)} cases...")

    for case_file in tqdm(case_files, desc="Processing cases"):
        case = Case.load_from_file(case_file)
        measurement = run_case(case)
        measurement.save_to_file(measurements_path)
        # Color mapping for scores
        colors = {0: "\033[91m", 1: "\033[93m", 2: "\033[33m", 3: "\033[92m"}  # red, orange, yellow, green
        reset_color = "\033[0m"
        bold = "\033[1m"

        score_color = colors.get(measurement.result.score, "")
        print(
            f"✨ Instruction '{case.instruction}' scored {bold}{score_color}{measurement.result.score}{reset_color} because '{measurement.result.reason}'\n"
        )


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
