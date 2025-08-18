from typing import Any

from .clay import run_instruction
from .judge import judge_instruction_achieved


def run_measurement(instruction: str) -> dict[str, Any]:
    """Run a single measurement: clear state -> run instruction -> judge result."""
    # Start with clear state
    initial_state = {"nodes": [], "edges": []}

    # Run the instruction
    final_state = run_instruction(initial_state, instruction)

    # Judge if instruction was achieved
    success = judge_instruction_achieved(instruction, final_state)

    return {"instruction": instruction, "initial_state": initial_state, "final_state": final_state, "success": success}


def process_multiple_instructions(instructions: list[str]) -> list[dict[str, Any]]:
    """Process multiple instructions and return results."""
    results = []
    for instruction in instructions:
        result = run_measurement(instruction)
        results.append(result)
    return results


if __name__ == "__main__":
    instruction = "Function node to add two numbers"
    result = run_measurement(instruction)
