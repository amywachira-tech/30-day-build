"""
search.py
Finds the chunks closest in meaning to a question, searching ONLY the
chunks the user's role is allowed to see.

Run after index.py:
    python search.py agent "cust bought sofa on sale 5 wks ago wants return, ok?"
    python search.py lead "can I approve a 400 dollar refund"
"""

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"
CHUNKS_FILE = Path("chunks.json")
EMBEDDINGS_FILE = Path("embeddings.npy")
TOP_K = 4

# Which access levels each role may see.
ALLOWED = {
    "agent": {"agent"},
    "lead": {"agent", "lead"},
}

_model = None


def get_model():
    """Load the model once and reuse it."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_index():
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    embeddings = np.load(EMBEDDINGS_FILE)
    if len(chunks) != len(embeddings):
        raise ValueError(
            "chunks.json and embeddings.npy are out of sync. Re-run index.py."
        )
    return chunks, embeddings


def is_in_force(chunk, as_of):
    """Exclude announcements that have expired or not yet taken effect."""
    expires = chunk.get("expires_on")
    if expires and date.fromisoformat(expires) < as_of:
        return False
    effective = chunk.get("effective_date")
    if chunk["source_type"] == "announcement" and effective:
        if date.fromisoformat(effective) > as_of:
            return False
    return True


def search(question, role, top_k=TOP_K, as_of=None):
    """Return the top_k (score, chunk) pairs the role is allowed to see."""
    if role not in ALLOWED:
        raise ValueError(f"unknown role '{role}'")
    as_of = as_of or date.today()
    chunks, embeddings = load_index()

    # Step 1: FILTER FIRST. Keep only chunks this role may see and that
    # are in force. Nothing else is searched.
    keep = [
        i for i, c in enumerate(chunks)
        if c["access_level"] in ALLOWED[role] and is_in_force(c, as_of)
    ]

    # Step 2: search only the kept chunks.
    query = get_model().encode([question], normalize_embeddings=True)[0]
    scores = embeddings[keep] @ query
    order = np.argsort(scores)[::-1][:top_k]
    results = [(float(scores[j]), chunks[keep[j]]) for j in order]

    # Step 3: safety check. Should never fire, because step 1 already filtered.
    for _, c in results:
        if c["access_level"] not in ALLOWED[role]:
            raise RuntimeError(f"access violation: {c['chunk_id']}")
    return results


def main():
    if len(sys.argv) != 3:
        print('Usage: python search.py agent "your question"')
        sys.exit(1)
    role, question = sys.argv[1], sys.argv[2]
    for score, c in search(question, role):
        first_line = c["text"].split("\n\n", 1)[-1].splitlines()[0]
        print(f"{score:.3f}  {c['chunk_id']:8} {c['access_level']:5} "
              f"tier {c['authority_tier']}  {c['source_name']}")
        print(f"        {first_line[:90]}")


if __name__ == "__main__":
    main()
