"""Tests for InMemoryBackend."""

from __future__ import annotations


from chengeta_ai.backends.memory_backend import InMemoryBackend


def test_set_and_get():
    b = InMemoryBackend()
    b.set("k", "v")
    assert b.get("k") == "v"


def test_miss_returns_none():
    b = InMemoryBackend()
    assert b.get("missing") is None


def test_delete():
    b = InMemoryBackend()
    b.set("k", "v")
    b.delete("k")
    assert b.get("k") is None


def test_exists():
    b = InMemoryBackend()
    b.set("k", "v")
    assert b.exists("k")
    b.delete("k")
    assert not b.exists("k")


def test_clear():
    b = InMemoryBackend()
    b.set("a", 1)
    b.set("b", 2)
    b.clear()
    assert b.get("a") is None
    assert b.get("b") is None


def test_ttl_expiry(monkeypatch):
    b = InMemoryBackend()
    base = 1000.0

    monkeypatch.setattr("chengeta_ai.backends.memory_backend.time.monotonic", lambda: base)
    b.set("k", "v", ttl=10)

    # Still within TTL
    monkeypatch.setattr("chengeta_ai.backends.memory_backend.time.monotonic", lambda: base + 9)
    assert b.get("k") == "v"

    # Past TTL
    monkeypatch.setattr("chengeta_ai.backends.memory_backend.time.monotonic", lambda: base + 11)
    assert b.get("k") is None


def test_lru_eviction():
    b = InMemoryBackend(max_size=3)
    b.set("a", 1)
    b.set("b", 2)
    b.set("c", 3)
    # Access 'a' to make it recently used
    b.get("a")
    # Adding 'd' should evict 'b' (LRU)
    b.set("d", 4)
    assert b.get("b") is None
    assert b.get("a") == 1
    assert b.get("c") == 3
    assert b.get("d") == 4


def test_stores_complex_values():
    b = InMemoryBackend()
    val = {"key": [1, 2, 3], "nested": {"x": True}}
    b.set("k", val)
    assert b.get("k") == val
