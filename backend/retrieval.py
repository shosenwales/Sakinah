"""
retrieval.py — embed a query and return top-k corpus entries by cosine similarity.

Embeddings are pre-normalised, so cosine similarity is just a dot product.
"""

import json
import pathlib
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = pathlib.Path(__file__).parent.parent
CORPUS_PATH = ROOT / "data" / "corpus.json"
EMBEDDINGS_PATH = ROOT / "data" / "embeddings.npy"
IDS_PATH = ROOT / "data" / "embedding_ids.json"

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None
_embeddings = None
_ids = None
_corpus_by_id = None


def _load():
    global _model, _embeddings, _ids, _corpus_by_id
    if _model is not None:
        return

    _model = SentenceTransformer(MODEL_NAME)

    _embeddings = np.load(EMBEDDINGS_PATH)

    with open(IDS_PATH, encoding="utf-8") as f:
        _ids = json.load(f)

    with open(CORPUS_PATH, encoding="utf-8") as f:
        corpus = json.load(f)
    _corpus_by_id = {entry["id"]: entry for entry in corpus}


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Return the top_k most similar corpus entries for a query string."""
    _load()

    query_vec = _model.encode([query], normalize_embeddings=True)
    scores = (_embeddings @ query_vec.T).squeeze()

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        entry = _corpus_by_id[_ids[idx]].copy()
        entry["score"] = float(scores[idx])
        results.append(entry)

    return results
