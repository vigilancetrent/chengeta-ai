---
title: "Configuration"
---

# Configuration

Chengeta AI can be configured programmatically or via environment variables.

---

## ChengetaSettings

The `ChengetaSettings` dataclass holds all configuration. Use it with `CacheManager.from_settings()`.

```python
from chengeta_ai import CacheManager, ChengetaSettings

# Programmatic configuration
settings = ChengetaSettings(
    backend="disk",
    disk_path="/data/cache",
    default_ttl=3600,
    namespace="myapp",
)
manager = CacheManager.from_settings(settings)
```

### All Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `backend` | `"memory" \| "disk" \| "redis"` | `"memory"` | Primary storage backend |
| `redis_url` | `str` | `"redis://localhost:6379/0"` | Redis connection URL |
| `disk_path` | `str` | `"/tmp/chengeta"` | Disk cache directory path |
| `default_ttl` | `int \| None` | `3600` | Default TTL in seconds (`None` = no expiry) |
| `semantic_threshold` | `float` | `0.95` | Minimum cosine similarity for semantic cache hit |
| `vector_backend` | `"faiss" \| "chroma" \| "none"` | `"none"` | Vector similarity backend |
| `embedding_dim` | `int` | `1536` | Embedding dimension (for FAISS) |
| `max_memory_entries` | `int` | `10000` | Max entries for InMemoryBackend |
| `key_hash_algo` | `"sha256" \| "md5"` | `"sha256"` | Hash algorithm for key generation |
| `namespace` | `str` | `"chengeta"` | Key prefix namespace |
| `ttl_embedding` | `int \| None` | `86400` | TTL for embedding cache (24h) |
| `ttl_retrieval` | `int \| None` | `3600` | TTL for retrieval cache (1h) |
| `ttl_context` | `int \| None` | `1800` | TTL for context cache (30min) |
| `ttl_response` | `int \| None` | `600` | TTL for response cache (10min) |

---

## Environment Variables

Every setting maps to an `CHENGETA_*` environment variable. Load them with `ChengetaSettings.from_env()`.

```python
from chengeta_ai import CacheManager, ChengetaSettings

manager = CacheManager.from_settings(ChengetaSettings.from_env())
```

| Variable | Default | Description |
|---|---|---|
| `CHENGETA_BACKEND` | `memory` | `memory`, `disk`, or `redis` |
| `CHENGETA_REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `CHENGETA_DISK_PATH` | `/tmp/chengeta` | Disk cache directory |
| `CHENGETA_DEFAULT_TTL` | `3600` | Seconds; `none` = no expiry |
| `CHENGETA_NAMESPACE` | `chengeta` | Key prefix |
| `CHENGETA_SEMANTIC_THRESHOLD` | `0.95` | Float 0-1 |
| `CHENGETA_VECTOR_BACKEND` | `none` | `faiss`, `chroma`, or `none` |
| `CHENGETA_EMBEDDING_DIM` | `1536` | Embedding dimension |
| `CHENGETA_MAX_MEMORY_ENTRIES` | `10000` | InMemoryBackend capacity |
| `CHENGETA_KEY_HASH_ALGO` | `sha256` | `sha256` or `md5` |
| `CHENGETA_TTL_EMBEDDING` | `86400` | Per-layer TTL |
| `CHENGETA_TTL_RETRIEVAL` | `3600` | Per-layer TTL |
| `CHENGETA_TTL_CONTEXT` | `1800` | Per-layer TTL |
| `CHENGETA_TTL_RESPONSE` | `600` | Per-layer TTL |

### Example

```bash
export CHENGETA_BACKEND=redis
export CHENGETA_REDIS_URL=redis://cache.internal:6379/0
export CHENGETA_DEFAULT_TTL=7200
export CHENGETA_NAMESPACE=prod
export CHENGETA_TTL_RESPONSE=300
```
