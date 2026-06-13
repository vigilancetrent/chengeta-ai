"""Tests for CacheKeyBuilder."""

from __future__ import annotations


from chengeta_ai.core.key_builder import CacheKeyBuilder


def test_key_schema():
    kb = CacheKeyBuilder(namespace="ns")
    key = kb.build("embedding", "hello world")
    parts = key.split(":")
    assert parts[0] == "ns"
    assert parts[1] == "embed"
    assert len(parts[2]) == 16


def test_deterministic():
    kb = CacheKeyBuilder()
    k1 = kb.build("response", "query text", extra={"model": "gpt-4"})
    k2 = kb.build("response", "query text", extra={"model": "gpt-4"})
    assert k1 == k2


def test_different_content_different_key():
    kb = CacheKeyBuilder()
    k1 = kb.build("response", "foo")
    k2 = kb.build("response", "bar")
    assert k1 != k2


def test_different_extra_different_key():
    kb = CacheKeyBuilder()
    k1 = kb.build("embedding", "text", extra={"model": "ada"})
    k2 = kb.build("embedding", "text", extra={"model": "3-small"})
    assert k1 != k2


def test_type_prefix_mapping():
    kb = CacheKeyBuilder(namespace="x")
    assert kb.build("retrieval", "q").startswith("x:retrieval:")
    assert kb.build("context", "s").startswith("x:ctx:")
    assert kb.build("response", "r").startswith("x:resp:")
    assert kb.build("embedding", "e").startswith("x:embed:")


def test_custom_type_prefix():
    kb = CacheKeyBuilder(namespace="x")
    key = kb.build("custom_type", "val")
    assert key.startswith("x:custom_type:")


def test_dict_order_invariant():
    kb = CacheKeyBuilder()
    k1 = kb.build("response", {"b": 2, "a": 1})
    k2 = kb.build("response", {"a": 1, "b": 2})
    assert k1 == k2
