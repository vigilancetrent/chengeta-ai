"""Tests for LLMMiddleware and AsyncLLMMiddleware."""

from __future__ import annotations

import pytest

from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.core.cache_manager import CacheManager
from chengeta_ai.core.key_builder import CacheKeyBuilder
from chengeta_ai.layers.response_cache import ResponseCache
from chengeta_ai.middleware.llm_middleware import LLMMiddleware, AsyncLLMMiddleware


@pytest.fixture
def response_cache():
    manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder(namespace="t"))
    return ResponseCache(manager)


@pytest.fixture
def key_builder():
    return CacheKeyBuilder(namespace="t")


def test_sync_middleware_caches(response_cache, key_builder):
    calls = []

    def llm(messages):
        calls.append(messages)
        return "answer"

    middleware = LLMMiddleware(response_cache, key_builder, model_id="gpt-4")
    wrapped = middleware(llm)

    messages = [{"role": "user", "content": "hello"}]
    r1 = wrapped(messages)
    r2 = wrapped(messages)

    assert r1 == r2 == "answer"
    assert len(calls) == 1


def test_sync_middleware_as_decorator(response_cache, key_builder):
    calls = []
    middleware = LLMMiddleware(response_cache, key_builder, model_id="gpt-4")

    @middleware
    def llm(messages):
        calls.append(1)
        return "result"

    llm([{"role": "user", "content": "q"}])
    llm([{"role": "user", "content": "q"}])
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_async_middleware_caches(response_cache, key_builder):
    calls = []

    async def async_llm(messages):
        calls.append(messages)
        return "async_answer"

    middleware = AsyncLLMMiddleware(response_cache, key_builder, model_id="gpt-4")
    wrapped = middleware(async_llm)

    messages = [{"role": "user", "content": "async test"}]
    r1 = await wrapped(messages)
    r2 = await wrapped(messages)

    assert r1 == r2 == "async_answer"
    assert len(calls) == 1
