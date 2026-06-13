---
title: "CacheManager"
---

# CacheManager

The `CacheManager` is the central orchestrator for all cache operations in Chengeta AI. It wires together a storage backend, key builder, TTL policy, optional vector backend, and invalidation engine into a single, coherent interface.

---

## Overview

Every cache read, write, deletion, and invalidation passes through `CacheManager`. It is responsible for:

- **Exact-match lookups** via the primary `CacheBackend`.
- **Semantic lookups** via an optional `VectorBackend` (cosine similarity search).
- **TTL resolution** using `TTLPolicy` to determine expiration per cache type.
- **Tag registration** so groups of keys can be invalidated together.
- **Lifecycle management** (clearing all entries, releasing resources).

You can construct a `CacheManager` manually by passing in each component, or use the `from_settings()` factory to build one from an `ChengetaSettings` dataclass.

---

## Usage

### Manual Construction

```python
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.core.cache_manager import CacheManager
from chengeta_ai.core.key_builder import CacheKeyBuilder
from chengeta_ai.core.policies import TTLPolicy

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="myapp"),
    ttl_policy=TTLPolicy(default_ttl=600),
)
```

### From Settings

```python
from chengeta_ai import CacheManager, ChengetaSettings

settings = ChengetaSettings(
    backend="redis",
    redis_url="redis://localhost:6379/0",
    namespace="prod",
)
manager = CacheManager.from_settings(settings)
```

### Basic Operations

```python
# Store a value with explicit TTL
manager.set("user:123:profile", {"name": "Alice"}, ttl=300)

# Retrieve
profile = manager.get("user:123:profile")

# Check existence
if manager.exists("user:123:profile"):
    print("Cache hit")

# Delete a single key
manager.delete("user:123:profile")

# Flush everything
manager.clear()
```

### Tag-Based Invalidation

```python
# Store entries with tags
manager.set("resp:a1b2", "Answer A", tags=["user:123", "model:gpt-4"])
manager.set("resp:c3d4", "Answer B", tags=["user:123", "model:gpt-4"])
manager.set("resp:e5f6", "Answer C", tags=["user:456", "model:gpt-4"])

# Invalidate all entries for user:123
removed = manager.invalidate("user:123")
print(f"Removed {removed} keys")  # 2
```

### Semantic Cache Lookup

```python
import numpy as np
from chengeta_ai.backends.vector_backend import FAISSBackend

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
    vector_backend=FAISSBackend(dim=1536),
    semantic_threshold=0.92,
)

embedding = np.random.rand(1536).astype(np.float32)
manager.set("embed:abc", "cached answer", vector=embedding)

# Semantic lookup -- finds nearest neighbor above threshold
query_vector = embedding + np.random.normal(0, 0.01, 1536).astype(np.float32)
result = manager.get("ignored", semantic=True, vector=query_vector)
```

:::tip[When to use semantic lookup]
Semantic cache is most useful for LLM response caching where slightly different prompts should return the same cached answer. Set `semantic_threshold` between 0.90 and 0.98 depending on how strict you want matching to be.
:::


---

## Factory: `from_settings`

The `from_settings()` classmethod constructs a fully-wired `CacheManager` from an `ChengetaSettings` instance. It handles backend selection, vector backend initialization, key builder configuration, and TTL policy setup automatically.

```python
from chengeta_ai import CacheManager, ChengetaSettings

# From environment variables
manager = CacheManager.from_settings(ChengetaSettings.from_env())

# Programmatic
manager = CacheManager.from_settings(ChengetaSettings(
    backend="disk",
    disk_path="/data/cache",
    vector_backend="faiss",
    embedding_dim=1536,
    semantic_threshold=0.93,
))
```

The factory selects backends based on the `backend` and `vector_backend` fields:

| `settings.backend` | Backend class |
|---|---|
| `"memory"` | `InMemoryBackend(max_size=settings.max_memory_entries)` |
| `"disk"` | `DiskBackend(directory=settings.disk_path)` |
| `"redis"` | `RedisBackend(url=settings.redis_url)` |

| `settings.vector_backend` | Vector backend class |
|---|---|
| `"none"` | `None` (disabled) |
| `"faiss"` | `FAISSBackend(dim=settings.embedding_dim)` |
| `"chroma"` | `ChromaBackend()` |

:::note
The factory always creates an `InvalidationEngine` backed by an `InMemoryBackend` for tag storage. This is separate from the primary cache backend.
:::


---

## API Reference

### Constructor

```python
CacheManager(
    backend: CacheBackend,
    key_builder: CacheKeyBuilder,
    ttl_policy: TTLPolicy | None = None,
    vector_backend: VectorBackend | None = None,
    invalidation_engine: InvalidationEngine | None = None,
    semantic_threshold: float = 0.95,
)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `backend` | `CacheBackend` | *required* | Primary key-value storage backend |
| `key_builder` | `CacheKeyBuilder` | *required* | Key construction helper |
| `ttl_policy` | `TTLPolicy \| None` | `None` | TTL rules per cache type; defaults to `TTLPolicy()` |
| `vector_backend` | `VectorBackend \| None` | `None` | Optional vector similarity backend for semantic search |
| `invalidation_engine` | `InvalidationEngine \| None` | `None` | Optional tag-based invalidation engine |
| `semantic_threshold` | `float` | `0.95` | Minimum cosine similarity for a semantic cache hit |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `get` | `get(key, semantic=False, vector=None)` | `Any \| None` | Retrieve a cached value (exact or semantic) |
| `set` | `set(key, value, ttl=None, vector=None, tags=None, cache_type="response")` | `None` | Store a value in the cache |
| `delete` | `delete(key)` | `None` | Remove a key from both primary and vector backends |
| `exists` | `exists(key)` | `bool` | Check if a key exists in the cache |
| `invalidate` | `invalidate(tag)` | `int` | Invalidate all keys associated with a tag |
| `clear` | `clear()` | `None` | Flush all cache entries from all backends |
| `close` | `close()` | `None` | Release all resources (connections, file handles) |
| `from_settings` | `from_settings(settings)` | `CacheManager` | Classmethod factory from `ChengetaSettings` |

### Properties

| Property | Type | Description |
|---|---|---|
| `key_builder` | `CacheKeyBuilder` | Access the key builder instance |
| `ttl_policy` | `TTLPolicy` | Access the TTL policy instance |

---

### Method Details

#### `get(key, semantic=False, vector=None)`

Retrieve a cached value by exact key or semantic similarity.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `key` | `str` | *required* | Cache key for exact lookup |
| `semantic` | `bool` | `False` | Enable nearest-neighbor lookup via vector backend |
| `vector` | `np.ndarray \| None` | `None` | Query embedding (required when `semantic=True`) |

When `semantic=True`, the method searches the vector backend for the nearest neighbor. If the best match has a cosine similarity score at or above `semantic_threshold`, the corresponding value is returned from the primary backend. Otherwise, `None` is returned.

:::warning
When `semantic=True`, both `vector_backend` and `vector` must be provided. If either is `None`, the method falls back to an exact key lookup.
:::


---

#### `set(key, value, ttl=None, vector=None, tags=None, cache_type="response")`

Store a value in the cache with optional TTL, vector indexing, and tag registration.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `key` | `str` | *required* | Cache key |
| `value` | `Any` | *required* | Value to store |
| `ttl` | `int \| None` | `None` | Explicit TTL in seconds; falls back to `TTLPolicy` |
| `vector` | `np.ndarray \| None` | `None` | Embedding vector to index alongside the key |
| `tags` | `list[str] \| None` | `None` | Invalidation tags to associate with the key |
| `cache_type` | `str` | `"response"` | Cache type used to resolve TTL from `TTLPolicy` |

:::tip[TTL Resolution Order]
1. If `ttl` is explicitly passed, that value is used.
2. Otherwise, `TTLPolicy.ttl_for(cache_type)` is consulted.
3. If the policy returns `None`, the entry never expires.
:::


---

#### `invalidate(tag)`

Remove all cache keys registered under the given tag. Returns `0` if no invalidation engine is configured.

```python
count = manager.invalidate("model:gpt-4")
print(f"Invalidated {count} cached responses")
```

---

## Next Steps

- [CacheKeyBuilder](key-builder.md) -- How keys are generated
- [Policies](policies.md) -- TTL and eviction configuration
- [InvalidationEngine](invalidation.md) -- Tag-based invalidation details
- [Settings](settings.md) -- Full configuration reference
