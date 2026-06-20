"""
build_index.py — precompute corpus embeddings and save to data/embeddings.npy.

Run once (or whenever corpus.json changes):
    python backend/build_index.py
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


def build():
    with open(CORPUS_PATH, encoding="utf-8") as f:
        corpus = json.load(f)

    # Index each passage by its translation plus the human-written context note and
    # theme labels. The displayed Arabic/translation stay verbatim; this only enriches
    # the matching representation so short or abstract verses still retrieve well for
    # emotional, first-person queries.
    def index_text(entry):
        parts = [entry["translation"], entry.get("context_note", "")]
        parts += entry.get("themes", [])
        return " ".join(p for p in parts if p)

    texts = [index_text(entry) for entry in corpus]
    ids = [entry["id"] for entry in corpus]

    print(f"Loading model {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Embedding {len(texts)} passages ...")
    vectors = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    np.save(EMBEDDINGS_PATH, vectors)
    with open(IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(ids, f)

    print(f"Saved {vectors.shape} embeddings to {EMBEDDINGS_PATH}")
    print(f"Saved aligned ids to {IDS_PATH}")


if __name__ == "__main__":
    build()
