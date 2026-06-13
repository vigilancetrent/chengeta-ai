"""Embedding call interception middleware."""

from __future__ import annotations

import asyncio
import functools
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

if TYPE_CHECKING:
    from chengeta_ai.layers.embedding_cache import EmbeddingCache


class EmbeddingMiddleware:
    """Wraps an embedding callable with EmbeddingCache.

    Usage::

        middleware = EmbeddingMiddleware(embedding_cache=ec, model_id="ada-002")

        @middleware
        def embed(text: str) -> np.ndarray:
            return openai_client.embed(text)

    Args:
        embedding_cache: EmbeddingCache instance.
        model_id: Model identifier for cache key discrimination.
    """

    def __init__(
        self,
        embedding_cache: "EmbeddingCache",
        model_id: str = "default",
    ) -> None:
        self._cache = embedding_cache
        self._model_id = model_id

    def __call__(self, embed_fn: Callable[[str], Any]) -> Callable[[str], np.ndarray]:
        if asyncio.iscoroutinefunction(embed_fn):

            @functools.wraps(embed_fn)
            async def async_wrapper(text: str) -> np.ndarray:
                cached = self._cache.get(text, self._model_id)
                if cached is not None:
                    return cached
                result = np.asarray(await embed_fn(text), dtype=np.float32)
                self._cache.set(text, result, self._model_id)
                return result

            return async_wrapper  # type: ignore[return-value]
        else:

            @functools.wraps(embed_fn)
            def sync_wrapper(text: str) -> np.ndarray:
                cached = self._cache.get(text, self._model_id)
                if cached is not None:
                    return cached
                result = np.asarray(embed_fn(text), dtype=np.float32)
                self._cache.set(text, result, self._model_id)
                return result

            return sync_wrapper

    def decorate(self, fn: Callable[[str], Any]) -> Callable[[str], np.ndarray]:
        return self(fn)
