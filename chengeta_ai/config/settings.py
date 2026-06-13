"""Configuration for chengeta-ai."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


@dataclass
class ChengetaSettings:
    """Central configuration object. All fields can be overridden via CHENGETA_* env vars."""

    backend: Literal["memory", "redis", "disk"] = "memory"
    redis_url: str = "redis://localhost:6379/0"
    disk_path: str = "/tmp/chengeta"
    default_ttl: int | None = 3600  # seconds; None = no expiry
    semantic_threshold: float = 0.95
    vector_backend: Literal["faiss", "chroma", "none"] = "none"
    embedding_dim: int = 1536  # matches OpenAI text-embedding-3-small
    max_memory_entries: int = 10_000
    key_hash_algo: Literal["sha256", "md5"] = "sha256"
    namespace: str = "chengeta"

    # Per-type TTL overrides (seconds)
    ttl_embedding: int | None = 86400  # 24h — embeddings rarely change
    ttl_retrieval: int | None = 3600  # 1h
    ttl_context: int | None = 1800  # 30min
    ttl_response: int | None = 600  # 10min — LLM responses expire fast

    @classmethod
    def from_env(cls) -> "ChengetaSettings":
        """Build settings from CHENGETA_* environment variables."""

        def _int_or_none(key: str, default: int | None) -> int | None:
            val = os.environ.get(key)
            if val is None:
                return default
            return None if val.lower() == "none" else int(val)

        return cls(
            backend=os.environ.get("CHENGETA_BACKEND", "memory"),  # type: ignore[arg-type]
            redis_url=os.environ.get("CHENGETA_REDIS_URL", "redis://localhost:6379/0"),
            disk_path=os.environ.get("CHENGETA_DISK_PATH", "/tmp/chengeta"),
            default_ttl=_int_or_none("CHENGETA_DEFAULT_TTL", 3600),
            semantic_threshold=float(os.environ.get("CHENGETA_SEMANTIC_THRESHOLD", "0.95")),
            vector_backend=os.environ.get("CHENGETA_VECTOR_BACKEND", "none"),  # type: ignore[arg-type]
            embedding_dim=int(os.environ.get("CHENGETA_EMBEDDING_DIM", "1536")),
            max_memory_entries=int(os.environ.get("CHENGETA_MAX_MEMORY_ENTRIES", "10000")),
            key_hash_algo=os.environ.get("CHENGETA_KEY_HASH_ALGO", "sha256"),  # type: ignore[arg-type]
            namespace=os.environ.get("CHENGETA_NAMESPACE", "chengeta"),
            ttl_embedding=_int_or_none("CHENGETA_TTL_EMBEDDING", 86400),
            ttl_retrieval=_int_or_none("CHENGETA_TTL_RETRIEVAL", 3600),
            ttl_context=_int_or_none("CHENGETA_TTL_CONTEXT", 1800),
            ttl_response=_int_or_none("CHENGETA_TTL_RESPONSE", 600),
        )
