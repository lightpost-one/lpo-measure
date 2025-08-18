from pathlib import Path

from .case import Case, CaseMeasurement
from .clay import run_case


def run_case_and_save(args: tuple[Path, Path]) -> CaseMeasurement:
    """Load a case, run it, save the measurement, and return the measurement."""
    case_file, measurements_path = args
    case = Case.load_from_file(case_file)
    measurement = run_case(case)
    measurement.save_to_file(measurements_path)
    # Color mapping for scores
    colors = {
        0: "\033[91m",
        1: "\033[93m",
        2: "\033[33m",
        3: "\033[92m",
    }  # red, orange, yellow, green
    reset_color = "\033[0m"
    bold = "\033[1m"

    score_color = colors.get(measurement.result.score, "")
    print(
        f"✨ Instruction '{case.instruction}' scored {bold}{score_color}{measurement.result.score}{reset_color} because '{measurement.result.reason}'\n"
    )
    return measurement
