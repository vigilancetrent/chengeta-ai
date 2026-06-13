"""Disk-based cache backend using diskcache."""

from __future__ import annotations

from typing import Any


class DiskBackend:
    """Persistent disk cache backed by diskcache.Cache.

    Survives process restarts. Safe for multi-process use (SQLite locking).
    TTL is handled natively by diskcache via the expire parameter.

    Args:
        directory: Path to the cache directory (created if absent).
        size_limit: Maximum cache size in bytes. Default: 1 GiB.
    """

    def __init__(self, directory: str, size_limit: int = 2**30) -> None:
        import diskcache  # core dependency — always available

        self._cache = diskcache.Cache(directory, size_limit=size_limit)

    def get(self, key: str) -> Any | None:
        return self._cache.get(key, default=None)

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._cache.set(key, value, expire=ttl)

    def delete(self, key: str) -> None:
        self._cache.delete(key)

    def exists(self, key: str) -> bool:
        return key in self._cache

    def clear(self) -> None:
        self._cache.clear()

    def close(self) -> None:
        self._cache.close()

    def __len__(self) -> int:
        return len(self._cache)
