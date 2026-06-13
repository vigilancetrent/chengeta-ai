---
title: "Core Setup"
---

# Core Setup

Get started with chengeta-ai using different backends and configurations.
No framework-specific extras are needed for core functionality.

```bash
pip install chengeta-ai
```

---

## 1.1 In-memory cache (zero config)

The simplest way to start -- an in-memory cache that requires no external services.

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder

manager = CacheManager(
    backend=InMemoryBackend(max_size=10_000),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)
```

---

## 1.2 Disk cache (survives process restarts)

Persist cached data to disk so it survives process restarts. Backed by SQLite via `diskcache`.

```python
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder

manager = CacheManager(
    backend=DiskBackend(directory="/var/cache/myapp"),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)
```

:::note
The `DiskBackend` accepts `directory` (not `path`) as its first argument.
:::


---

## 1.3 From environment variables

Configure the cache entirely through environment variables -- useful for containerised deployments.

```bash
export CHENGETA_BACKEND=redis
export CHENGETA_REDIS_URL=redis://localhost:6379/0
export CHENGETA_DEFAULT_TTL=3600
export CHENGETA_NAMESPACE=myapp
```

```python
from chengeta_ai import CacheManager, ChengetaSettings

manager = CacheManager.from_settings(ChengetaSettings.from_env())
```

---

## 1.4 With full TTL policy per layer

Set different time-to-live values for each cache layer so embeddings, retrieval results,
session context, and LLM responses each expire at the right cadence.

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, TTLPolicy

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="myapp"),
    ttl_policy=TTLPolicy(
        default_ttl=3600,
        per_type={
            "embed": 86_400,      # embeddings last 24 h
            "retrieval": 3_600,   # retrieval results last 1 h
            "context": 1_800,     # session context 30 min
            "response": 600,      # LLM responses 10 min
        },
    ),
)
```

---

## 1.5 With tag-based invalidation

Attach tags to cached entries and invalidate groups of related entries in a single call.

```python
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder, InvalidationEngine
)

tag_store = InMemoryBackend()
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="myapp"),
    invalidation_engine=InvalidationEngine(tag_store),
)
```
