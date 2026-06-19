"""
compose.py — template-based response composition.

Picks a template for the primary theme of the top retrieved passage,
slots in the verbatim translation and reference, and appends the disclaimer.
No text is generated or paraphrased — only the template wrapper changes.
"""

import json
import pathlib
import random

ROOT = pathlib.Path(__file__).parent.parent
TEMPLATES_PATH = ROOT / "data" / "templates.json"

_templates = None

DISCLAIMER = (
    "Sakinah is not a substitute for a qualified scholar, imam, or licensed "
    "mental health professional. For serious concerns, please consult a qualified person."
)

FALLBACK_TEMPLATE = (
    "Here is a passage that may offer some comfort:\n\n"
    '"{translation}"\n— {reference}'
)


def _load():
    global _templates
    if _templates is None:
        with open(TEMPLATES_PATH, encoding="utf-8") as f:
            _templates = json.load(f)


def compose(retrieved: list[dict]) -> dict:
    """
    Build a response from the top retrieved passage.
    Returns {"response": str, "sources": list[dict], "is_crisis": False, "disclaimer": str}.
    """
    _load()

    if not retrieved:
        return {
            "response": "I'm here with you. Could you tell me a little more about what you're feeling?",
            "sources": [],
            "is_crisis": False,
            "disclaimer": DISCLAIMER,
        }

    top = retrieved[0]
    theme = top["themes"][0] if top["themes"] else None

    template_str = _pick_template(theme)
    response_text = template_str.format(
        translation=top["translation"],
        reference=top["reference"],
    )

    sources = [
        {
            "id": entry["id"],
            "source_type": entry["source_type"],
            "reference": entry["reference"],
            "themes": entry["themes"],
            "score": entry.get("score", 0.0),
        }
        for entry in retrieved
    ]

    return {
        "response": response_text,
        "sources": sources,
        "is_crisis": False,
        "disclaimer": DISCLAIMER,
    }


def _pick_template(theme: str | None) -> str:
    if theme and theme in _templates:
        options = _templates[theme]
        return random.choice(options)["template"]
    return FALLBACK_TEMPLATE
