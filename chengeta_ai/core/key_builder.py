"""Cache key construction with canonical hashing."""

from __future__ import annotations

import hashlib
import json
from typing import Any


_TYPE_PREFIXES: dict[str, str] = {
    "embedding": "embed",
    "retrieval": "retrieval",
    "context": "ctx",
    "response": "resp",
}


class CacheKeyBuilder:
    """Builds deterministic, namespaced cache keys.

    Key schema: ``{namespace}:{type_prefix}:{hash[:16]}``

    The hash is computed over a canonical JSON representation of the content,
    ensuring identical inputs always produce identical keys regardless of
    dict key ordering or float precision drift.

    Args:
        namespace: Global prefix applied to every key (default: 'chengeta').
        algo: Hash algorithm — 'sha256' (default, secure) or 'md5' (faster).
    """

    def __init__(self, namespace: str = "chengeta", algo: str = "sha256") -> None:
        self._namespace = namespace
        self._algo = algo

    def build(
        self,
        cache_type: str,
        content: Any,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Build a cache key for the given cache type and content.

        Args:
            cache_type: One of 'embedding', 'retrieval', 'context', 'response',
                        or a custom string (used as the prefix as-is).
            content: The primary cache input (text, list, dict, etc.).
            extra: Additional discriminators (e.g. model_id, index_version).

        Returns:
            A string key like 'chengeta:embed:a3f9b2c1d4e5f678'.
        """
        prefix = _TYPE_PREFIXES.get(cache_type, cache_type)
        payload = self._canonicalize(content, extra)
        digest = hashlib.new(self._algo, payload.encode()).hexdigest()[:16]
        return f"{self._namespace}:{prefix}:{digest}"

    def _canonicalize(self, content: Any, extra: dict[str, Any] | None) -> str:
        obj: dict[str, Any] = {"content": content}
        if extra:
            obj["extra"] = extra
        return json.dumps(obj, sort_keys=True, ensure_ascii=True, default=str)
