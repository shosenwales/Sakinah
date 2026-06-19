"""
safety.py — distress detection.

Runs before retrieval. Returns a crisis response dict if any crisis pattern
matches, otherwise returns None so the normal flow continues.
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent.parent
CRISIS_PATH = ROOT / "data" / "crisis.json"

_crisis_data = None


def _load():
    global _crisis_data
    if _crisis_data is None:
        with open(CRISIS_PATH, encoding="utf-8") as f:
            _crisis_data = json.load(f)


def check(query: str) -> dict | None:
    """
    Returns a crisis dict if the query matches any distress pattern,
    or None if it is safe to proceed with normal retrieval.
    """
    _load()

    q = query.lower()

    for _category, patterns in _crisis_data["patterns"].items():
        for pattern in patterns:
            if re.search(re.escape(pattern), q):
                return _build_crisis_response()

    return None


def _build_crisis_response() -> dict:
    cr = _crisis_data["crisis_response"]
    helplines = _crisis_data["helplines"]

    helpline_lines = []
    for h in helplines:
        helpline_lines.append(f"{h['name']}: {h['number']} ({h['available']})")

    response_text = (
        f"{cr['heading']}\n\n"
        f"{cr['message']}\n\n"
        + "\n".join(helpline_lines)
        + f"\n\n{cr['prompt_scholar']}"
    )

    return {
        "response": response_text,
        "sources": [],
        "is_crisis": True,
        "disclaimer": _disclaimer(),
    }


def _disclaimer() -> str:
    return (
        "Sakinah is not a substitute for a qualified scholar, imam, or licensed "
        "mental health professional. If you are in distress, please seek immediate help."
    )
