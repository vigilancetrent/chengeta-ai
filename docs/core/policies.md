# Policies

Chengeta AI provides two policy dataclasses that control cache expiration and eviction behavior: `TTLPolicy` for time-based expiration and `EvictionPolicy` for capacity-based eviction.

---

## Overview

Caching without expiration leads to stale data; caching without eviction leads to unbounded memory growth. The policy system gives you fine-grained control over both:

- **TTLPolicy** lets you set a global default TTL and override it per cache type (embeddings, retrievals, contexts, responses).
- **EvictionPolicy** defines how entries are removed when capacity limits are reached (LRU or TTL-only).

Both are plain Python dataclasses -- lightweight, easy to construct, and easy to serialize.

---

## TTLPolicy

### What It Does

`TTLPolicy` determines how long cached entries survive. It supports a global default and per-cache-type overrides, so embeddings (which rarely change) can live for 24 hours while LLM responses (which may be volatile) expire in 10 minutes.

### Usage

#### Basic TTL Configuration

```python
from chengeta_ai.core.policies import TTLPolicy

# Default: 1 hour for everything
policy = TTLPolicy()
print(policy.ttl_for("response"))  # 3600

# Custom default
policy = TTLPolicy(default_ttl=1800)
print(policy.ttl_for("anything"))  # 1800

# No expiry
policy = TTLPolicy(default_ttl=None)
print(policy.ttl_for("response"))  # None
```

#### Per-Type Overrides

```python
policy = TTLPolicy(
    default_ttl=3600,
    per_type={
        "embedding": 86400,   # 24 hours
        "retrieval": 3600,    # 1 hour
        "context": 1800,      # 30 minutes
        "response": 600,      # 10 minutes
    },
)

print(policy.ttl_for("embedding"))  # 86400
print(policy.ttl_for("response"))   # 600
print(policy.ttl_for("custom"))     # 3600 (falls back to default)
```

#### From Settings

```python
from chengeta_ai.config.settings import ChengetaSettings
from chengeta_ai.core.policies import TTLPolicy

settings = ChengetaSettings(
    default_ttl=7200,
    ttl_embedding=172800,
    ttl_response=300,
)
policy = TTLPolicy.from_settings(settings)

print(policy.ttl_for("embedding"))  # 172800
print(policy.ttl_for("response"))   # 300
print(policy.ttl_for("retrieval"))  # 3600 (from settings default)
```

!!! tip "Recommended TTLs by cache type"
    | Cache Type | Recommended TTL | Rationale |
    |---|---|---|
    | `embedding` | 24h (86400s) | Embeddings rarely change for the same input text |
    | `retrieval` | 1h (3600s) | Retrieved documents may be updated periodically |
    | `context` | 30min (1800s) | Agent context is session-scoped and evolves quickly |
    | `response` | 10min (600s) | LLM responses may vary and should stay fresh |

### API Reference {#ttlpolicy-api}

#### Constructor

```python
@dataclass
class TTLPolicy:
    default_ttl: int | None = 3600
    per_type: dict[str, int | None] = field(default_factory=dict)
```

| Field | Type | Default | Description |
|---|---|---|---|
| `default_ttl` | `int \| None` | `3600` | Fallback TTL in seconds; `None` means no expiry |
| `per_type` | `dict[str, int \| None]` | `{}` | Cache type to TTL mapping (overrides `default_ttl`) |

#### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `ttl_for` | `ttl_for(cache_type)` | `int \| None` | Return the effective TTL for the given cache type |
| `from_settings` | `from_settings(settings)` | `TTLPolicy` | Classmethod: build from an `ChengetaSettings` instance |

#### `ttl_for(cache_type)`

Returns the TTL for a specific cache type. Checks `per_type` first; if the type is not found, returns `default_ttl`.

| Parameter | Type | Description |
|---|---|---|
| `cache_type` | `str` | The cache type to look up (e.g., `"response"`, `"embedding"`) |

#### `from_settings(settings)`

Builds a `TTLPolicy` from an `ChengetaSettings` instance, mapping settings fields to per-type TTLs:

| Settings Field | Cache Type |
|---|---|
| `settings.default_ttl` | `default_ttl` |
| `settings.ttl_embedding` | `"embedding"` |
| `settings.ttl_retrieval` | `"retrieval"` |
| `settings.ttl_context` | `"context"` |
| `settings.ttl_response` | `"response"` |

---

## EvictionPolicy

### What It Does

`EvictionPolicy` configures how entries are removed when capacity limits are reached. It supports LRU (least-recently-used) eviction or TTL-only expiry (no active eviction).

!!! note
    Eviction enforcement depends on backend support. Not all backends implement capacity-based eviction. The `EvictionPolicy` is a configuration object -- the backend decides how to honor it.

### Usage

```python
from chengeta_ai.core.policies import EvictionPolicy

# LRU with a max of 10,000 entries
policy = EvictionPolicy(
    strategy="lru",
    max_entries=10_000,
)

# TTL-only (no active eviction, entries expire naturally)
policy = EvictionPolicy(
    strategy="ttl_only",
)

# LRU with both entry and byte limits
policy = EvictionPolicy(
    strategy="lru",
    max_entries=50_000,
    max_bytes=500 * 1024 * 1024,  # 500 MB
)
```

### Strategies

=== "LRU"

    Least-recently-used eviction removes the oldest-accessed entries when capacity is exceeded.

    ```python
    policy = EvictionPolicy(
        strategy="lru",
        max_entries=10_000,
    )
    ```

    Best for: general-purpose caching where recent entries are more valuable.

=== "TTL Only"

    No active eviction. Entries are only removed when they expire or are explicitly deleted.

    ```python
    policy = EvictionPolicy(
        strategy="ttl_only",
    )
    ```

    Best for: caches with well-defined TTLs and predictable memory usage.

!!! warning
    Using `strategy="ttl_only"` without setting TTLs on your entries can cause unbounded memory growth. Always pair it with a `TTLPolicy` that has a finite `default_ttl`.

### API Reference {#evictionpolicy-api}

#### Constructor

```python
@dataclass
class EvictionPolicy:
    strategy: Literal["lru", "ttl_only"] = "lru"
    max_entries: int | None = None
    max_bytes: int | None = None
```

| Field | Type | Default | Description |
|---|---|---|---|
| `strategy` | `"lru" \| "ttl_only"` | `"lru"` | Eviction strategy |
| `max_entries` | `int \| None` | `None` | Maximum number of entries before eviction; `None` means unlimited |
| `max_bytes` | `int \| None` | `None` | Maximum total size in bytes; `None` means unlimited (backend-dependent) |

---

## Combining Policies

TTL and eviction policies work together. TTL controls when individual entries expire; eviction controls what happens when capacity limits are hit.

```python
from chengeta_ai.core.policies import TTLPolicy, EvictionPolicy

ttl = TTLPolicy(
    default_ttl=3600,
    per_type={"embedding": 86400, "response": 600},
)

eviction = EvictionPolicy(
    strategy="lru",
    max_entries=50_000,
)

# Pass both to CacheManager
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.core.cache_manager import CacheManager
from chengeta_ai.core.key_builder import CacheKeyBuilder

manager = CacheManager(
    backend=InMemoryBackend(max_size=eviction.max_entries),
    key_builder=CacheKeyBuilder(),
    ttl_policy=ttl,
)
```

---

## Next Steps

- [CacheManager](cache-manager.md) -- Uses policies for TTL resolution
- [Settings](settings.md) -- Configure TTLs via environment variables
- [InvalidationEngine](invalidation.md) -- Manual invalidation alongside TTL expiry
