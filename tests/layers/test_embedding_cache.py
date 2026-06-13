"""Tests for EmbeddingCache."""

from __future__ import annotations

import numpy as np
import pytest

from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.core.cache_manager import CacheManager
from chengeta_ai.core.key_builder import CacheKeyBuilder
from chengeta_ai.layers.embedding_cache import EmbeddingCache


@pytest.fixture
def ec():
    manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder(namespace="t"))
    return EmbeddingCache(manager, dim=4)


def test_miss_returns_none(ec):
    assert ec.get("hello", "m1") is None


def test_set_and_get(ec):
    vec = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
    ec.set("hello", vec, "m1")
    result = ec.get("hello", "m1")
    assert result is not None
    np.testing.assert_array_almost_equal(result, vec)


def test_different_models_different_entries(ec):
    vec1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    vec2 = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
    ec.set("hello", vec1, "model-a")
    ec.set("hello", vec2, "model-b")
    np.testing.assert_array_almost_equal(ec.get("hello", "model-a"), vec1)
    np.testing.assert_array_almost_equal(ec.get("hello", "model-b"), vec2)


def test_get_or_compute_calls_fn_on_miss(ec):
    calls = []

    def compute(text):
        calls.append(text)
        return np.zeros(4, dtype=np.float32)

    ec.get_or_compute("query", compute, "m1")
    assert len(calls) == 1
    # Second call should be a cache hit
    ec.get_or_compute("query", compute, "m1")
    assert len(calls) == 1
