from .case import Case, CaseMeasurement
from .clay import run_case
from .run import BenchmarkRun


def run_case_and_save(case: Case, run: BenchmarkRun) -> CaseMeasurement:
    """Load a case, run it, save the measurement, and return the measurement."""
    measurement = run_case(case, run)
    if run.id is None:
        raise ValueError("BenchmarkRun must have an id to save measurements.")
    measurement.save_to_db(run.id)
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
        f"✨ Instruction '{bold}{case.instruction}{reset_color}' scored {bold}{score_color}{measurement.result.score}{reset_color} because '{measurement.result.reason}'\n"
    )
    return measurement
