"""Chengeta AI cache setup for the RAG pipeline.

Three active layers:
  EmbeddingCache  — text -> vector     (skip OpenRouter embed API)
  RetrievalCache  — query -> doc list  (skip FAISS search)
  ResponseCache   — messages -> answer (skip OpenRouter LLM)

Backend: TieredBackend (InMemory L1 + DiskBackend L2) — survives restarts.
"""

from __future__ import annotations

from pathlib import Path

from chengeta_ai.backends.disk_backend import DiskBackend
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.backends.tiered_backend import TieredBackend
from chengeta_ai.core.cache_manager import CacheManager
from chengeta_ai.core.key_builder import CacheKeyBuilder
from chengeta_ai.core.policies import TTLPolicy
from chengeta_ai.layers.embedding_cache import EmbeddingCache
from chengeta_ai.layers.response_cache import ResponseCache
from chengeta_ai.layers.retrieval_cache import RetrievalCache

_CACHE_DIR = Path.home() / ".cache" / "rag-openrouter"


def build_cache_manager() -> CacheManager:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CacheManager(
        backend=TieredBackend(
            l1=InMemoryBackend(max_size=2_000),
            l2=DiskBackend(str(_CACHE_DIR / "store")),
            l1_ttl=600,
        ),
        key_builder=CacheKeyBuilder(namespace="rag"),
        ttl_policy=TTLPolicy(
            default_ttl=3_600,
            per_type={
                "embedding": 86_400 * 7,  # 7 days
                "retrieval": 3_600,
                "response": 86_400,
            },
        ),
    )


def build_layers(
    manager: CacheManager,
) -> tuple[EmbeddingCache, RetrievalCache, ResponseCache]:
    # dim=1 placeholder — EmbeddingCache.get() uses frombuffer which
    # auto-sizes from bytes, so dim is irrelevant at read time.
    return (
        EmbeddingCache(manager, dim=1),
        RetrievalCache(manager),
        ResponseCache(manager),
    )
