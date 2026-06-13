"""Tests for DiskBackend."""

from __future__ import annotations


from chengeta_ai.backends.disk_backend import DiskBackend


def test_set_and_get(tmp_path):
    b = DiskBackend(str(tmp_path / "cache"))
    b.set("k", "hello")
    assert b.get("k") == "hello"
    b.close()


def test_miss(tmp_path):
    b = DiskBackend(str(tmp_path / "cache"))
    assert b.get("nope") is None
    b.close()


def test_delete(tmp_path):
    b = DiskBackend(str(tmp_path / "cache"))
    b.set("k", "v")
    b.delete("k")
    assert b.get("k") is None
    b.close()


def test_exists(tmp_path):
    b = DiskBackend(str(tmp_path / "cache"))
    b.set("k", "v")
    assert b.exists("k")
    b.delete("k")
    assert not b.exists("k")
    b.close()


def test_clear(tmp_path):
    b = DiskBackend(str(tmp_path / "cache"))
    b.set("a", 1)
    b.set("b", 2)
    b.clear()
    assert b.get("a") is None
    b.close()


def test_persistence(tmp_path):
    path = str(tmp_path / "cache")
    b = DiskBackend(path)
    b.set("k", {"data": [1, 2, 3]})
    b.close()
    # Re-open same path
    b2 = DiskBackend(path)
    assert b2.get("k") == {"data": [1, 2, 3]}
    b2.close()
