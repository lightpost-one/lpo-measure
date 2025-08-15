# LPO Measure

## Project Setup

This project uses `uv` to manage the Python environment.

1.  **Install `uv`**: If you don't have `uv` installed, follow the [official installation instructions](https://astral.sh/docs/uv#installation).

2.  **Create and activate the virtual environment**:
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    uv pip install -r requirements.txt
    ```

## Call node tool

This approach calls the Node.js script directly using an absolute path while setting the correct working directory. Here's the key setup:

```python
import subprocess
import json

def run_canvas_cli(state, prompt, electron_terminal_path):
    result = subprocess.run([
        'node', f'{electron_terminal_path}/dist-headless/run-headless.mjs',
        '--state', json.dumps(state),
        '--prompt', prompt
    ], 
    capture_output=True, 
    text=True,
    cwd=electron_terminal_path,  # Critical: sets working directory
    stderr=subprocess.DEVNULL    # Suppresses error messages
    )
    
    return json.loads(result.stdout)

# Usage
state = {"nodes": [], "edges": []}
result = run_canvas_cli(state, "Create a function", "/path/to/electron-terminal")
```

**Key points:**
- Set `cwd=electron_terminal_path` so the script can find its dependencies
- Use `stderr=subprocess.DEVNULL` to suppress checkpoint errors  
- Returns clean JSON that you can parse directly
- No npm overhead, just pure Node.js execution
- Works from any Python project location
