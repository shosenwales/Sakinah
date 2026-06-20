"""
compose.py — template-based response composition.

Picks a template for the primary theme of the top retrieved passage and wraps
the passage in empathetic framing: an `intro` before it and an `outro` after.
The passage itself (verbatim Arabic, translation, reference) is returned as
structured data so the front end can render it as a styled verse card.
No source text is generated or paraphrased — only the framing changes.
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

FALLBACK_TEMPLATE = {
    "intro": "Here is a passage that may offer some comfort:",
    "outro": "",
}


def _load():
    global _templates
    if _templates is None:
        with open(TEMPLATES_PATH, encoding="utf-8") as f:
            _templates = json.load(f)


def compose(retrieved: list[dict]) -> dict:
    """
    Build a response from the top retrieved passage.
    Returns {"response", "outro", "passage", "sources", "is_crisis", "disclaimer"}.
    `passage` carries the verbatim Arabic/translation/reference for the verse card,
    or None when there is nothing to show.
    """
    _load()

    if not retrieved:
        return {
            "response": "I'm here with you. Could you tell me a little more about what you're feeling?",
            "outro": "",
            "passage": None,
            "sources": [],
            "is_crisis": False,
            "disclaimer": DISCLAIMER,
        }

    top = retrieved[0]
    theme = top["themes"][0] if top["themes"] else None
    template = _pick_template(theme)

    passage = {
        "arabic": top["arabic"],
        "translation": top["translation"],
        "reference": top["reference"],
        "source_type": top["source_type"],
    }

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
        "response": template["intro"],
        "outro": template["outro"],
        "passage": passage,
        "sources": sources,
        "is_crisis": False,
        "disclaimer": DISCLAIMER,
    }


def _pick_template(theme: str | None) -> dict:
    if theme and theme in _templates:
        return random.choice(_templates[theme])
    return FALLBACK_TEMPLATE
