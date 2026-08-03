"""
Small stateless helper functions used across the app.
"""
import json
import re
import uuid


def new_session_id() -> str:
    return uuid.uuid4().hex


def safe_json_loads(text: str, default=None):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def extract_json_block(text: str) -> str:
    """
    Pulls a JSON object/array out of a model response that may be
    wrapped in markdown code fences or extra prose.
    """
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence_match:
        return fence_match.group(1).strip()

    brace_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if brace_match:
        return brace_match.group(1).strip()

    return text.strip()
