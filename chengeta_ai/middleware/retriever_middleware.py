"""Retriever call interception middleware."""

from __future__ import annotations

import asyncio
import functools
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from chengeta_ai.layers.retrieval_cache import RetrievalCache


class RetrieverMiddleware:
    """Wraps a retriever callable with RetrievalCache.

    Usage::

        middleware = RetrieverMiddleware(retrieval_cache=rc, retriever_id="pinecone")

        @middleware
        def retrieve(query: str, top_k: int) -> list:
            return pinecone_index.query(query, top_k=top_k)

    Args:
        retrieval_cache: RetrievalCache instance.
        retriever_id: Identifier used to distinguish different retriever sources.
        default_top_k: Default top_k value if not passed to the wrapped function.
    """

    def __init__(
        self,
        retrieval_cache: "RetrievalCache",
        retriever_id: str = "default",
        default_top_k: int = 5,
    ) -> None:
        self._cache = retrieval_cache
        self._retriever_id = retriever_id
        self._default_top_k = default_top_k

    def __call__(self, retrieve_fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(retrieve_fn):

            @functools.wraps(retrieve_fn)
            async def async_wrapper(query: str, top_k: int | None = None, **kwargs: Any) -> Any:
                k = top_k if top_k is not None else self._default_top_k
                cached = self._cache.get(query, self._retriever_id, k)
                if cached is not None:
                    return cached
                result = await retrieve_fn(query, k, **kwargs)
                self._cache.set(query, result, self._retriever_id, k)
                return result

            return async_wrapper
        else:

            @functools.wraps(retrieve_fn)
            def sync_wrapper(query: str, top_k: int | None = None, **kwargs: Any) -> Any:
                k = top_k if top_k is not None else self._default_top_k
                cached = self._cache.get(query, self._retriever_id, k)
                if cached is not None:
                    return cached
                result = retrieve_fn(query, k, **kwargs)
                self._cache.set(query, result, self._retriever_id, k)
                return result

            return sync_wrapper

    def decorate(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        return self(fn)
