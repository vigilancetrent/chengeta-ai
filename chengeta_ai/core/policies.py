"""TTL and eviction policies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class TTLPolicy:
    """TTL configuration with per-cache-type overrides.

    Args:
        default_ttl: Fallback TTL in seconds. None means no expiry.
        per_type: Dict of cache_type → TTL seconds (overrides default_ttl).
    """

    default_ttl: int | None = 3600
    per_type: dict[str, int | None] = field(default_factory=dict)

    def ttl_for(self, cache_type: str) -> int | None:
        """Return the effective TTL for the given cache type."""
        if cache_type in self.per_type:
            return self.per_type[cache_type]
        return self.default_ttl

    @classmethod
    def from_settings(cls, settings: object) -> "TTLPolicy":
        """Build TTLPolicy from an ChengetaSettings instance."""
        return cls(
            default_ttl=getattr(settings, "default_ttl", 3600),
            per_type={
                "embedding": getattr(settings, "ttl_embedding", 86400),
                "retrieval": getattr(settings, "ttl_retrieval", 3600),
                "context": getattr(settings, "ttl_context", 1800),
                "response": getattr(settings, "ttl_response", 600),
            },
        )


@dataclass
class EvictionPolicy:
    """Eviction strategy configuration.

    Args:
        strategy: LRU (least-recently-used) or ttl_only (pure TTL expiry).
        max_entries: Maximum number of entries before eviction kicks in.
        max_bytes: Maximum total size in bytes (backend-dependent support).
    """

    strategy: Literal["lru", "ttl_only"] = "lru"
    max_entries: int | None = None
    max_bytes: int | None = None
