import os
import subprocess
import tempfile
import time

import orjson
from dotenv import load_dotenv

from .case import Case, CaseMeasurement
from .judge import judge_instruction_achieved

load_dotenv()
CLAY_CLI_PATH = os.getenv("CLAY_CLI_PATH")
if not CLAY_CLI_PATH:
    raise ValueError("CLAY_CLI_PATH environment variable not set")


def run_case(case: Case) -> CaseMeasurement:
    """Run instruction on canvas and return a CaseResult with the measurement."""
    # Start with clear state

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json"
        ) as state_file, tempfile.NamedTemporaryFile(
            mode="r", suffix=".json"
        ) as output_file:
            state_file.write(orjson.dumps(case.initial_state).decode())
            state_file.flush()

            start_time = time.time()
            result = subprocess.run(
                [
                    "node",
                    f"{CLAY_CLI_PATH}",
                    "--state-file",
                    state_file.name,
                    "--prompt",
                    case.instruction,
                    "--output",
                    output_file.name,
                ],
                capture_output=True,
                text=True,
            )
            end_time = time.time()
            clay_runtime = end_time - start_time
            result.check_returncode()

            output = output_file.read()
            if not output:
                final_state = None
            else:
                final_state = orjson.loads(output)
    except (Exception, subprocess.CalledProcessError):
        final_state = None
        clay_runtime = 0.0

    start_time = time.time()
    judge_result = judge_instruction_achieved(case.instruction, final_state)
    end_time = time.time()
    judge_runtime = end_time - start_time

    return CaseMeasurement.create(
        case, final_state, judge_result, clay_runtime, judge_runtime
    )
