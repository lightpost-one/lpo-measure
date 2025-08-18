from typing import Any

import litellm
import orjson
from dotenv import load_dotenv

load_dotenv()

litellm.api_base = "https://app.lyngby.lightpost.one/"
litellm.api_key = "9e571bf73904"


def judge_instruction_achieved(instruction: str, final_state: dict[str, Any]) -> dict[str, Any]:
    """Use LLM to evaluate how well the instruction was achieved based on final state."""
    system_prompt = """You are an expert evaluator that judges how well user instructions were completed on a canvas interface.

Your task is to analyze the final state of a canvas and determine how successfully a user's instruction was fulfilled.

Evaluation criteria:
- Score 0: Instruction completely failed or ignored
- Score 1: Minimal progress, major elements missing or incorrect
- Score 2: Good progress, instruction mostly completed with minor issues
- Score 3: Perfect completion, instruction fully achieved as intended

You must respond with valid JSON in this exact format:
{
  "score": <0-3>,
  "reason": "<explanation in 100 words or less>"
}

Focus on whether the final canvas state matches what the user requested. Consider node types, content, positioning, relationships, and overall structure."""

    user_prompt = f"""Instruction: "{instruction}"

Final canvas state:
{orjson.dumps(final_state, option=orjson.OPT_INDENT_2).decode()}"""

    try:
        response = litellm.completion(
            model="gpt-5",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content  # type: ignore
        assert content is not None
        return orjson.loads(content)
    except Exception as e:
        print(f"LLM judge error: {e}")
        return {"score": 0, "reason": f"Error during evaluation: {e}"}
