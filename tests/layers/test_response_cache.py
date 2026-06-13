"""Tests for ResponseCache."""

from __future__ import annotations

import pytest

from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.core.cache_manager import CacheManager
from chengeta_ai.core.key_builder import CacheKeyBuilder
from chengeta_ai.layers.response_cache import ResponseCache


@pytest.fixture
def rc():
    from chengeta_ai.core.invalidation import InvalidationEngine

    tag_store = InMemoryBackend()
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="t"),
        invalidation_engine=InvalidationEngine(tag_store),
    )
    return ResponseCache(manager)


MESSAGES = [{"role": "user", "content": "What is 2+2?"}]


def test_miss(rc):
    assert rc.get(MESSAGES, "gpt-4") is None


def test_set_and_get(rc):
    rc.set(MESSAGES, "4", "gpt-4")
    assert rc.get(MESSAGES, "gpt-4") == "4"


def test_different_models_independent(rc):
    rc.set(MESSAGES, "gpt4-answer", "gpt-4")
    assert rc.get(MESSAGES, "gpt-3.5") is None


def test_different_params_independent(rc):
    rc.set(MESSAGES, "answer-temp0", "gpt-4", params={"temperature": 0})
    assert rc.get(MESSAGES, "gpt-4", params={"temperature": 1}) is None


def test_get_or_generate_caches(rc):
    calls = []

    def gen(msgs):
        calls.append(msgs)
        return "cached!"

    result1 = rc.get_or_generate(MESSAGES, gen, "gpt-4")
    result2 = rc.get_or_generate(MESSAGES, gen, "gpt-4")
    assert result1 == result2 == "cached!"
    assert len(calls) == 1


def test_invalidate_model(rc):
    rc.set(MESSAGES, "v", "gpt-4", tags=["model:gpt-4"])
    count = rc.invalidate_model("gpt-4")
    assert count >= 1
