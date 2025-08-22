import logging
import subprocess
import tempfile
import time

import orjson

from .case import Case, CaseMeasurement
from .judge import judge_instruction_achieved
from .run import BenchmarkRun

logger = logging.getLogger(__name__)


def run_case(case: Case, run: BenchmarkRun) -> CaseMeasurement:
    """Run instruction on canvas and return a CaseResult with the measurement."""
    # Start with clear state
    final_state = None
    clay_runtime = 0.0
    with (
        tempfile.NamedTemporaryFile(mode="w", suffix=".json") as state_file,
        tempfile.NamedTemporaryFile(mode="r", suffix=".json") as output_file,
    ):
        cmd = [
            "node",
            f"{run.script_path}",
            "--state",
            state_file.name,
            "--prompt",
            f"'{case.instruction}'",
            "--output",
            output_file.name,
            "--model-name",
            run.model,
        ]
        try:
            state_file.write(orjson.dumps(case.initial_state).decode())
            state_file.flush()

            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )
            result.check_returncode()
            clay_runtime = time.time() - start_time

            output = output_file.read()
            if output:
                final_state = orjson.loads(output)
        except Exception:
            logger.error(f'\nError from calling "{" ".join(cmd)}"\n')

    start_time = time.time()
    judge_result = judge_instruction_achieved(case.instruction, final_state)
    end_time = time.time()
    judge_runtime = end_time - start_time

    return CaseMeasurement.create(case, final_state, judge_result, clay_runtime, judge_runtime)
