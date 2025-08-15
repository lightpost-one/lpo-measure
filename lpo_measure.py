import subprocess
import json
import os

def run_canvas_cli(state, prompt, electron_terminal_path):
    result = subprocess.run([
        'node', f'{electron_terminal_path}/dist-headless/run-headless.mjs',
        '--state', json.dumps(state),
        '--prompt', prompt
    ], 
    capture_output=True, 
    text=True,
    cwd=electron_terminal_path  # Critical: sets working directory
    )
    
    return json.loads(result.stdout)

if __name__ == '__main__':
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    # Get the electron terminal path from the environment variable
    electron_terminal_path = os.getenv("ELECTRON_TERMINAL_PATH")

    if not electron_terminal_path:
        raise ValueError("ELECTRON_TERMINAL_PATH environment variable not set")

    # Usage
    state = {"nodes": [], "edges": []}
    result = run_canvas_cli(state, "Create a function", electron_terminal_path)
    print(result)
