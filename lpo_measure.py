import os
import subprocess

import orjson


def run_canvas_cli(state, prompt, electron_terminal_path):
    result = subprocess.run(
        [
            "node",
            f"{electron_terminal_path}/dist-headless/run-headless.mjs",
            "--state",
            orjson.dumps(state).decode(),
            "--prompt",
            prompt,
        ],
        capture_output=True,
        text=True,
        cwd=electron_terminal_path,
    )

    return orjson.loads(result.stdout)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    electron_terminal_path = os.getenv("ELECTRON_TERMINAL_PATH")
    if not electron_terminal_path:
        raise ValueError("ELECTRON_TERMINAL_PATH environment variable not set")

    state = {"nodes": [], "edges": []}
    result = run_canvas_cli(state, "Create a function", electron_terminal_path)
    print(result)
