"""
index.py
Turns every chunk in chunks.json into an embedding (a list of numbers that
captures its meaning) and saves them to embeddings.npy.

Run after chunk.py:  python index.py
The first run downloads the model (about 90 MB). Later runs reuse it.
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
CHUNKS_FILE = Path("chunks.json")
EMBEDDINGS_FILE = Path("embeddings.npy")


def main():
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    texts = [c["text"] for c in chunks]

    model = SentenceTransformer(MODEL_NAME)
    # normalize_embeddings=True lets search use a simple dot product
    # as the similarity score (1.0 = identical meaning).
    embeddings = model.encode(texts, normalize_embeddings=True)

    np.save(EMBEDDINGS_FILE, embeddings)
    print(f"Embedded {len(chunks)} chunks, {embeddings.shape[1]} numbers each")
    print(f"Written to {EMBEDDINGS_FILE}")


if __name__ == "__main__":
    main()
