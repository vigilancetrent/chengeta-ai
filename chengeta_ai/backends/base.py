"""Protocol definitions for cache backends."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class CacheBackend(Protocol):
    """Structural interface all key-value backends must satisfy."""

    def get(self, key: str) -> Any | None:
        """Return cached value, or None if missing/expired."""
        ...

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store value under key. ttl is seconds; None means no expiry."""
        ...

    def delete(self, key: str) -> None:
        """Remove key. No-op if not present."""
        ...

    def exists(self, key: str) -> bool:
        """Return True if key is present and not expired."""
        ...

    def clear(self) -> None:
        """Flush all entries."""
        ...

    def close(self) -> None:
        """Release resources (connections, file handles)."""
        ...


@runtime_checkable
class VectorBackend(Protocol):
    """Structural interface for vector similarity backends."""

    def add(self, key: str, vector: np.ndarray, metadata: dict[str, Any]) -> None:
        """Index a vector under the given key."""
        ...

    def search(self, vector: np.ndarray, top_k: int = 1) -> list[tuple[str, float]]:
        """Return list of (key, similarity_score) for the top_k nearest neighbors."""
        ...

    def delete(self, key: str) -> None:
        """Remove a vector by key."""
        ...

    def clear(self) -> None:
        """Remove all vectors."""
        ...

    def close(self) -> None:
        """Release resources."""
        ...
