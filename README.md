# LPO Measure

## Setup

1.  **Install `uv`**: [Official installation instructions](https://astral.sh/docs/uv#installation).
2.  **Set environment variable**: Create a `.env` file with the following content:
    ```
    ELECTRON_TERMINAL_PATH=/path/to/your/electron-terminal
    ```
3.  **Set up environment**:
    ```bash
    make venv
    ```

## Usage

```bash
make run
```

This will call the headless node script and print the JSON output.
