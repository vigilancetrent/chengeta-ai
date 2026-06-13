"""Tag-based cache invalidation engine."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chengeta_ai.backends.base import CacheBackend


_TAG_PREFIX = "__tag__:"


class InvalidationEngine:
    """Tag-based invalidation: associate keys with tags, invalidate by tag.

    Each key can be registered with one or more string tags.
    Calling ``invalidate_tag()`` removes all keys that share that tag.

    The tag→key mapping is stored in a secondary CacheBackend (typically
    an InMemoryBackend). This avoids polluting the primary cache namespace.

    Args:
        tag_store: Backend used to persist tag→key mappings.
    """

    def __init__(self, tag_store: "CacheBackend") -> None:
        self._store = tag_store

    def register(self, key: str, tags: list[str]) -> None:
        """Associate a cache key with one or more tags."""
        for tag in tags:
            tag_key = f"{_TAG_PREFIX}{tag}"
            existing_raw = self._store.get(tag_key)
            existing: list[str] = json.loads(existing_raw) if existing_raw else []
            if key not in existing:
                existing.append(key)
            self._store.set(tag_key, json.dumps(existing))

    def invalidate_tag(self, tag: str, backend: "CacheBackend") -> int:
        """Remove all cache keys registered under the given tag.

        Args:
            tag: The tag to invalidate.
            backend: The primary cache backend to delete keys from.

        Returns:
            Number of keys invalidated.
        """
        tag_key = f"{_TAG_PREFIX}{tag}"
        raw = self._store.get(tag_key)
        if not raw:
            return 0
        keys: list[str] = json.loads(raw)
        for key in keys:
            backend.delete(key)
        self._store.delete(tag_key)
        return len(keys)

    def invalidate_key(self, key: str, backend: "CacheBackend") -> None:
        """Remove a specific key from the primary backend."""
        backend.delete(key)
