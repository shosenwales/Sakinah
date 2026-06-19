"""
test_retrieval.py — verify that retrieval rankings make sense with placeholder corpus.

Run from the project root:
    python -m pytest tests/ -v
"""

import pathlib
import sys

# Ensure backend is importable when running from the project root.
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))

import pytest
from retrieval import retrieve


THEME_QUERIES = [
    ("I feel so anxious and cannot stop worrying", "anxiety"),
    ("I am grieving and struggling with loss", "loss"),
    ("I want to be more grateful for what I have", "gratitude"),
    ("I feel hopeless and need hope", "hope"),
    ("I find it hard to be patient", "patience"),
    ("I need forgiveness for my sins", "forgiveness"),
]


@pytest.mark.parametrize("query,expected_theme", THEME_QUERIES)
def test_top_result_theme(query, expected_theme):
    """The top-1 result for a theme-labelled query should belong to that theme."""
    results = retrieve(query, top_k=3)
    assert len(results) > 0, f"No results returned for query: {query!r}"
    top = results[0]
    assert expected_theme in top["themes"], (
        f"Query {query!r}: expected theme '{expected_theme}', "
        f"got top result id={top['id']} themes={top['themes']} score={top['score']:.3f}"
    )


def test_returns_top_k():
    results = retrieve("I am feeling sad", top_k=3)
    assert len(results) == 3


def test_scores_are_descending():
    results = retrieve("help me with patience", top_k=3)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True), "Scores should be in descending order"


def test_result_schema():
    results = retrieve("anxiety and worry", top_k=1)
    r = results[0]
    for key in ("id", "source_type", "reference", "themes", "translation", "score"):
        assert key in r, f"Missing key '{key}' in result"
