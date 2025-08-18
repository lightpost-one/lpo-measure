import argparse
from pathlib import Path

from tqdm import tqdm

from lpo_measure.clay import run_instruction

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
    measurements_path = Path("measurements")

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
        case_result = run_instruction(case)
        case_result.save_to_file(measurements_path)

        score = "PASS" if case_result.success else "FAIL"
        print(f"{score}: {case.instruction}")


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
        # Default behavior for backwards compatibility
        instruction = "Function node to add two numbers"
        case = Case.create(instruction)
        result = run_instruction(case)
        print(f"Success: {result.success}, Instruction: {result.instruction}")
