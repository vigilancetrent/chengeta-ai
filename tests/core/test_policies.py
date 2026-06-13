"""Tests for TTLPolicy and EvictionPolicy."""

from __future__ import annotations

from chengeta_ai.core.policies import TTLPolicy, EvictionPolicy


def test_default_ttl():
    p = TTLPolicy(default_ttl=3600)
    assert p.ttl_for("response") == 3600
    assert p.ttl_for("embedding") == 3600


def test_per_type_override():
    p = TTLPolicy(default_ttl=3600, per_type={"embedding": 86400, "response": 600})
    assert p.ttl_for("embedding") == 86400
    assert p.ttl_for("response") == 600
    assert p.ttl_for("context") == 3600  # falls back to default


def test_none_ttl():
    p = TTLPolicy(default_ttl=None)
    assert p.ttl_for("response") is None


def test_eviction_defaults():
    e = EvictionPolicy()
    assert e.strategy == "lru"
    assert e.max_entries is None
