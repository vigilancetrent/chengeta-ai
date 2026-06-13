"""Redis cache backend (optional dependency)."""

from __future__ import annotations

import pickle
from typing import Any

try:
    import redis as _redis_lib

    _REDIS_AVAILABLE = True
except ImportError:
    _redis_lib = None  # type: ignore[assignment]
    _REDIS_AVAILABLE = False


class RedisBackend:
    """Redis-backed cache. Requires the 'redis' extra.

    Install with: pip install 'chengeta-ai[redis]'

    Args:
        url: Redis connection URL (e.g. 'redis://localhost:6379/0').
        key_prefix: Prefix applied to all keys (default: empty).
    """

    def __init__(self, url: str = "redis://localhost:6379/0", key_prefix: str = "") -> None:
        if not _REDIS_AVAILABLE:
            raise ImportError(
                "RedisBackend requires the 'redis' package. "
                "Install it with: pip install 'chengeta-ai[redis]'"
            )
        self._client = _redis_lib.from_url(url, decode_responses=False)
        self._prefix = key_prefix

    def _k(self, key: str) -> str:
        return f"{self._prefix}{key}" if self._prefix else key

    def get(self, key: str) -> Any | None:
        raw = self._client.get(self._k(key))
        return pickle.loads(raw) if raw is not None else None  # noqa: S301

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._client.set(self._k(key), pickle.dumps(value), ex=ttl)

    def delete(self, key: str) -> None:
        self._client.delete(self._k(key))

    def exists(self, key: str) -> bool:
        return bool(self._client.exists(self._k(key)))

    def clear(self) -> None:
        if self._prefix:
            keys = self._client.keys(f"{self._prefix}*")
            if keys:
                self._client.delete(*keys)
        else:
            self._client.flushdb()

    def close(self) -> None:
        self._client.close()
