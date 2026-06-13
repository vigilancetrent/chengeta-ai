"""LLM call interception middleware."""

from __future__ import annotations

import asyncio
import functools
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from chengeta_ai.core.key_builder import CacheKeyBuilder
    from chengeta_ai.layers.response_cache import ResponseCache


class LLMMiddleware:
    """Wraps any synchronous LLM callable with response caching.

    Usage::

        middleware = LLMMiddleware(response_cache=rc, key_builder=kb)

        @middleware
        def call_llm(messages):
            return openai_client.chat(messages)

        # Or wrap at call time:
        cached_fn = middleware(original_llm_fn)

    Args:
        response_cache: ResponseCache instance.
        key_builder: CacheKeyBuilder instance.
        model_id: Model identifier used as a key discriminator.
    """

    def __init__(
        self,
        response_cache: "ResponseCache",
        key_builder: "CacheKeyBuilder",
        model_id: str = "default",
    ) -> None:
        self._cache = response_cache
        self._kb = key_builder
        self._model_id = model_id

    def __call__(self, llm_fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(llm_fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            messages = args[0] if args else kwargs.get("messages", list(args))
            if not isinstance(messages, list):
                messages = [str(messages)]
            cached = self._cache.get(messages, model_id=self._model_id)
            if cached is not None:
                return cached
            result = llm_fn(*args, **kwargs)
            self._cache.set(messages, result, model_id=self._model_id)
            return result

        return wrapper

    def decorate(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        return self(fn)


class AsyncLLMMiddleware:
    """Wraps any async LLM callable with response caching.

    Automatically detects coroutine functions and wraps them appropriately.

    Args:
        response_cache: ResponseCache instance.
        key_builder: CacheKeyBuilder instance.
        model_id: Model identifier used as a key discriminator.
    """

    def __init__(
        self,
        response_cache: "ResponseCache",
        key_builder: "CacheKeyBuilder",
        model_id: str = "default",
    ) -> None:
        self._cache = response_cache
        self._kb = key_builder
        self._model_id = model_id

    def __call__(self, llm_fn: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(llm_fn):

            @functools.wraps(llm_fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                messages = args[0] if args else kwargs.get("messages", [])
                if not isinstance(messages, list):
                    messages = [str(messages)]
                cached = self._cache.get(messages, model_id=self._model_id)
                if cached is not None:
                    return cached
                result = await llm_fn(*args, **kwargs)
                self._cache.set(messages, result, model_id=self._model_id)
                return result

            return async_wrapper
        else:

            @functools.wraps(llm_fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                messages = args[0] if args else kwargs.get("messages", [])
                if not isinstance(messages, list):
                    messages = [str(messages)]
                cached = self._cache.get(messages, model_id=self._model_id)
                if cached is not None:
                    return cached
                result = llm_fn(*args, **kwargs)
                self._cache.set(messages, result, model_id=self._model_id)
                return result

            return sync_wrapper

    def decorate(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        return self(fn)
