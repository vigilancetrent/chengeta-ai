"""Tests for InvalidationEngine."""

from __future__ import annotations

from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.core.invalidation import InvalidationEngine


def test_register_and_invalidate():
    tag_store = InMemoryBackend()
    backend = InMemoryBackend()
    engine = InvalidationEngine(tag_store)

    backend.set("k1", "v1")
    backend.set("k2", "v2")
    engine.register("k1", ["tag_a"])
    engine.register("k2", ["tag_a", "tag_b"])

    count = engine.invalidate_tag("tag_a", backend)
    assert count == 2
    assert backend.get("k1") is None
    assert backend.get("k2") is None


def test_invalidate_nonexistent_tag():
    tag_store = InMemoryBackend()
    backend = InMemoryBackend()
    engine = InvalidationEngine(tag_store)
    count = engine.invalidate_tag("missing_tag", backend)
    assert count == 0


def test_invalidate_key_directly():
    tag_store = InMemoryBackend()
    backend = InMemoryBackend()
    engine = InvalidationEngine(tag_store)

    backend.set("k", "v")
    engine.invalidate_key("k", backend)
    assert backend.get("k") is None
