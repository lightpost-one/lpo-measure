import os
import subprocess

import orjson
from dotenv import load_dotenv

from .case import Case, CaseResult
from .judge import judge_instruction_achieved

load_dotenv()
ELECTRON_TERMINAL_PATH = os.getenv("ELECTRON_TERMINAL_PATH")
if not ELECTRON_TERMINAL_PATH:
    raise ValueError("ELECTRON_TERMINAL_PATH environment variable not set")


def run_instruction(case: Case) -> CaseResult:
    """Run instruction on canvas and return a CaseResult with the measurement."""
    # Start with clear state
    initial_state = {"nodes": [], "edges": []}

    try:
        result = subprocess.run(
            [
                "node",
                f"{ELECTRON_TERMINAL_PATH}/dist-headless/run-headless.mjs",
                "--state",
                orjson.dumps(initial_state).decode(),
                "--prompt",
                case.instruction,
            ],
            capture_output=True,
            text=True,
            cwd=ELECTRON_TERMINAL_PATH,
        )

        final_state = orjson.loads(result.stdout)
    except Exception:
        final_state = None

    # Judge the result
    judge_result = judge_instruction_achieved(case.instruction, final_state)
    success = judge_result.get("score", 0) > 0

    return CaseResult.create(
        case=case,
        initial_state=initial_state,
        final_state=final_state,
        success=success,
    )
