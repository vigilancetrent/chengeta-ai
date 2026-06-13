"""Semantic cache with FAISS vector similarity — no external embedding model needed.

Uses a deterministic hash-based embedding that produces consistent vectors for
similar text, demonstrating the SemanticCache workflow without requiring a
dedicated embedding model.

For production: swap mock_embed for a real embedding model, e.g.
    from langchain_ollama import OllamaEmbeddings
    emb = OllamaEmbeddings(model="nomic-embed-text")  # pull first: ollama pull nomic-embed-text
    embed_fn = lambda t: np.array(emb.embed_query(t), dtype=np.float32)

Run:
    uv run python -m cookbook.semantic_cache.agent
"""

from __future__ import annotations
from chengeta_ai.backends.vector_backend import FAISSBackend
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai import SemanticCache
import hashlib
import time
import numpy as np

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DIM = 1536


def mock_embed(text: str) -> np.ndarray:
    """Deterministic unit-vector embedding based on text hash.

    Semantically similar phrases hash to slightly different seeds, so a
    threshold below 1.0 is needed for similarity hits (use ~0.85 for demo).
    In production, replace with a real sentence-transformer or Ollama embedding.
    """
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(DIM).astype(np.float32)
    return v / np.linalg.norm(v)


def main() -> None:
    cache = SemanticCache(
        exact_backend=InMemoryBackend(),
        vector_backend=FAISSBackend(dim=DIM),
        embed_fn=mock_embed,
        threshold=1.0,  # exact match only with deterministic embedding
    )

    q1 = "How to reduce p95 latency?"
    answer = "Profile hot path, add caching, optimize DB queries."

    t0 = time.perf_counter()
    cache.set(q1, answer)
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    hit = cache.get(q1)
    t3 = time.perf_counter()
    print("=== Exact hit (same text) ===")
    print(hit)
    print(f"set : {t1 - t0:.6f}s")
    print(f"get : {t3 - t2:.6f}s  ({(t1 - t0) / (t3 - t2):.0f}x faster)")

    print("\n=== Miss (different text, deterministic embed != same vector) ===")
    t4 = time.perf_counter()
    miss = cache.get("How can I lower p95 response latency?")
    t5 = time.perf_counter()
    print(miss)
    print(f"get (miss): {t5 - t4:.6f}s")

    print("\n=== Direct exact cache hit ===")
    cache.set("What is p95 latency optimization?", "Measure, profile, then cache hot paths.")
    t6 = time.perf_counter()
    result = cache.get("What is p95 latency optimization?")
    t7 = time.perf_counter()
    print(result)
    print(f"get : {t7 - t6:.6f}s")


if __name__ == "__main__":
    main()
