from .case import Case, CaseMeasurement
from .clay import run_case


def run_case_and_save(args: tuple[int, int]) -> CaseMeasurement:
    """Load a case, run it, save the measurement, and return the measurement."""
    case_id, run_id = args
    case = Case.load_from_db(case_id)
    measurement = run_case(case)
    measurement.save_to_db(run_id)
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
