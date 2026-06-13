"""Embedding cache layer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import numpy as np

if TYPE_CHECKING:
    from chengeta_ai.core.cache_manager import CacheManager


class EmbeddingCache:
    """Cache layer for text embeddings.

    Stores numpy arrays by serialising to raw bytes. On retrieval,
    bytes are deserialised back to float32 arrays of the original dimension.

    Args:
        manager: Underlying CacheManager instance.
        dim: Embedding dimension (needed for deserialisation).
    """

    def __init__(self, manager: "CacheManager", dim: int = 1536) -> None:
        self._manager = manager
        self._dim = dim

    def get(self, text: str, model_id: str = "default") -> np.ndarray | None:
        """Retrieve a cached embedding, or None on miss."""
        key = self._manager.key_builder.build("embedding", text, extra={"model": model_id})
        raw = self._manager.get(key)
        if raw is None:
            return None
        return np.frombuffer(raw, dtype=np.float32).copy()

    def set(
        self,
        text: str,
        vector: np.ndarray,
        model_id: str = "default",
        ttl: int | None = None,
    ) -> None:
        """Store an embedding in the cache."""
        key = self._manager.key_builder.build("embedding", text, extra={"model": model_id})
        self._manager.set(
            key,
            vector.astype(np.float32).tobytes(),
            ttl=ttl,
            cache_type="embedding",
        )

    def get_or_compute(
        self,
        text: str,
        compute_fn: Callable[[str], np.ndarray],
        model_id: str = "default",
        ttl: int | None = None,
    ) -> np.ndarray:
        """Return cached embedding or compute, cache, and return it."""
        cached = self.get(text, model_id)
        if cached is not None:
            return cached
        vector = compute_fn(text)
        self.set(text, vector, model_id, ttl)
        return vector
