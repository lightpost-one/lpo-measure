import os
import subprocess
from typing import Any

import orjson
from dotenv import load_dotenv

load_dotenv()
ELECTRON_TERMINAL_PATH = os.getenv("ELECTRON_TERMINAL_PATH")
if not ELECTRON_TERMINAL_PATH:
    raise ValueError("ELECTRON_TERMINAL_PATH environment variable not set")


def run_instruction(state: dict[str, Any], instruction: str) -> dict[str, Any]:
    """Run instruction on canvas and return the resulting state."""
    result = subprocess.run(
        [
            "node",
            f"{ELECTRON_TERMINAL_PATH}/dist-headless/run-headless.mjs",
            "--state",
            orjson.dumps(state).decode(),
            "--prompt",
            instruction,
        ],
        capture_output=True,
        text=True,
        cwd=ELECTRON_TERMINAL_PATH,
    )

    return orjson.loads(result.stdout)
