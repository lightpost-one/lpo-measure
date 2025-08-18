import os
import subprocess
import time

import orjson
from dotenv import load_dotenv

from .case import Case, CaseMeasurement
from .judge import judge_instruction_achieved

load_dotenv()
ELECTRON_TERMINAL_PATH = os.getenv("ELECTRON_TERMINAL_PATH")
if not ELECTRON_TERMINAL_PATH:
    raise ValueError("ELECTRON_TERMINAL_PATH environment variable not set")


def run_case(case: Case) -> CaseMeasurement:
    """Run instruction on canvas and return a CaseResult with the measurement."""
    # Start with clear state

    try:
        start_time = time.time()
        result = subprocess.run(
            [
                "node",
                f"{ELECTRON_TERMINAL_PATH}/dist-headless/run-headless.mjs",
                "--state",
                orjson.dumps(case.initial_state).decode(),
                "--prompt",
                case.instruction,
            ],
            capture_output=True,
            text=True,
            cwd=ELECTRON_TERMINAL_PATH,
        )
        end_time = time.time()
        runtime = end_time - start_time

        final_state = orjson.loads(result.stdout)
    except Exception:
        final_state = None
        runtime = 0.0

    judge_result = judge_instruction_achieved(case.instruction, final_state)

    return CaseMeasurement.create(case, final_state, judge_result, runtime)
