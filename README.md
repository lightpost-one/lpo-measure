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

### Running measurements

```bash
make run
```

This runs measurements against all cases in the `cases/` directory with progress reporting.

### Adding test cases

Create a plaintext file with instructions (one per line), then:

```bash
uv run -m lpo_measure add instructions.txt
```

This creates JSON case files in the `cases/` directory, with filenames based on instruction hashes.
