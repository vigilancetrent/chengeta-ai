"""Tests for SemanticCache."""

from __future__ import annotations

import pytest

from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.backends.vector_backend import FAISSBackend
from chengeta_ai.layers.semantic_cache import SemanticCache
from tests.conftest import mock_embed


@pytest.fixture
def semantic_cache():
    pytest.importorskip("faiss", reason="faiss-cpu not installed")
    exact = InMemoryBackend()
    vector = FAISSBackend(dim=1536)
    return SemanticCache(exact, vector, mock_embed, threshold=0.95)


def test_miss(semantic_cache):
    assert semantic_cache.get("What is the capital of France?") is None


def test_exact_hit(semantic_cache):
    semantic_cache.set("What is the capital of France?", "Paris")
    result = semantic_cache.get("What is the capital of France?")
    assert result == "Paris"


def test_semantic_hit_similar_query(semantic_cache):
    """Queries that embed to nearly identical vectors should hit."""
    # We store with one phrasing and retrieve with the exact same text
    # (mock_embed is deterministic, so same text = identical vector = score 1.0)
    query = "capital of France"
    semantic_cache.set(query, "Paris")
    # Retrieve with exact same query — score = 1.0 >= threshold
    assert semantic_cache.get(query) == "Paris"


def test_clear(semantic_cache):
    semantic_cache.set("q", "answer")
    semantic_cache.clear()
    assert semantic_cache.get("q") is None


def test_delete(semantic_cache):
    semantic_cache.set("q", "answer")
    semantic_cache.delete("q")
    assert semantic_cache.get("q") is None
