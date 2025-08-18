import argparse
from pathlib import Path
from typing import Any

from tqdm import tqdm

from .case import Case
from .clay import run_instruction
from .judge import judge_instruction_achieved


def run_measurement(instruction: str) -> dict[str, Any]:
    """Run a single measurement: clear state -> run instruction -> judge result."""
    # Start with clear state
    initial_state = {"nodes": [], "edges": []}

    # Run the instruction
    final_state = run_instruction(initial_state, instruction)

    # Judge if instruction was achieved
    success = judge_instruction_achieved(instruction, final_state)

    return {"instruction": instruction, "initial_state": initial_state, "final_state": final_state, "success": success}


def process_multiple_instructions(instructions: list[str]) -> list[dict[str, Any]]:
    """Process multiple instructions and return results."""
    results = []
    for instruction in instructions:
        result = run_measurement(instruction)
        results.append(result)
    return results


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
        case.save_to_file(cases_path)
        print(f"Created case: {case.hash} - {instruction}")


def run_all_cases() -> None:
    """Run measurements against all cases in the cases folder."""
    cases_path = Path("cases")

    if not cases_path.exists():
        print("No cases directory found")
        return

    case_files = list(cases_path.glob("*.json"))

    if not case_files:
        print("No cases found")
        return

    print(f"Running {len(case_files)} cases...")

    for case_file in tqdm(case_files, desc="Processing cases"):
        case = Case.load_from_file(case_file)
        result = run_measurement(case.instruction)
        score = "PASS" if result["success"] else "FAIL"
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
        result = run_measurement(instruction)
        print(result)
