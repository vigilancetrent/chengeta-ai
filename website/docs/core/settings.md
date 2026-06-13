---
title: "ChengetaSettings"
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ChengetaSettings

`ChengetaSettings` is a dataclass that centralizes every configuration knob in Chengeta AI. It can be constructed programmatically or loaded from `CHENGETA_*` environment variables.

---

## Overview

Managing cache configuration across backends, TTLs, namespaces, and vector stores can quickly become scattered. `ChengetaSettings` provides a single source of truth:

- All fields have sensible defaults, so you can start with `ChengetaSettings()` and override only what you need.
- The `from_env()` classmethod reads `CHENGETA_*` environment variables, making it easy to configure caching per deployment without code changes.
- Pass the settings object to `CacheManager.from_settings()` to get a fully-wired cache manager in one call.

---

## Usage

### Programmatic Configuration

```python
from chengeta_ai.config.settings import ChengetaSettings

# All defaults -- in-memory backend, 1h TTL, no vector backend
settings = ChengetaSettings()

# Customized for production
settings = ChengetaSettings(
    backend="redis",
    redis_url="redis://cache.internal:6379/0",
    namespace="prod",
    default_ttl=7200,
    ttl_response=300,
    vector_backend="faiss",
    embedding_dim=1536,
    semantic_threshold=0.93,
)
```

### From Environment Variables

```python
from chengeta_ai.config.settings import ChengetaSettings

settings = ChengetaSettings.from_env()
```

Set the environment variables before running your application:

<Tabs>
<TabItem value="bash" label="Bash">

```bash
export CHENGETA_BACKEND=redis
export CHENGETA_REDIS_URL=redis://cache.internal:6379/0
export CHENGETA_NAMESPACE=prod
export CHENGETA_DEFAULT_TTL=7200
export CHENGETA_TTL_RESPONSE=300
export CHENGETA_VECTOR_BACKEND=faiss
export CHENGETA_EMBEDDING_DIM=1536
export CHENGETA_SEMANTIC_THRESHOLD=0.93
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="docker" label="Docker">

```dockerfile
ENV CHENGETA_BACKEND=redis
ENV CHENGETA_REDIS_URL=redis://cache:6379/0
ENV CHENGETA_NAMESPACE=prod
ENV CHENGETA_DEFAULT_TTL=7200
ENV CHENGETA_TTL_RESPONSE=300
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="-env-file" label=".env file">

```dotenv
CHENGETA_BACKEND=redis
CHENGETA_REDIS_URL=redis://cache.internal:6379/0
CHENGETA_NAMESPACE=prod
CHENGETA_DEFAULT_TTL=7200
CHENGETA_TTL_RESPONSE=300
CHENGETA_VECTOR_BACKEND=faiss
CHENGETA_EMBEDDING_DIM=1536
```

</TabItem>

</Tabs>


:::tip
Use a `.env` file with a library like `python-dotenv` to keep environment variables organized during development. Call `dotenv.load_dotenv()` before `ChengetaSettings.from_env()`.
:::


### Wiring to CacheManager

```python
from chengeta_ai import CacheManager, ChengetaSettings

# One-line production setup
manager = CacheManager.from_settings(ChengetaSettings.from_env())

# Or with explicit settings
manager = CacheManager.from_settings(ChengetaSettings(
    backend="disk",
    disk_path="/data/cache",
))
```

---

## Configuration Fields

### Backend Selection

| Field | Type | Default | Description |
|---|---|---|---|
| `backend` | `"memory" \| "redis" \| "disk"` | `"memory"` | Primary storage backend |
| `redis_url` | `str` | `"redis://localhost:6379/0"` | Redis connection URL (used when `backend="redis"`) |
| `disk_path` | `str` | `"/tmp/chengeta"` | Directory path for disk cache (used when `backend="disk"`) |
| `max_memory_entries` | `int` | `10000` | Maximum entries for `InMemoryBackend` |

### Key Generation

| Field | Type | Default | Description |
|---|---|---|---|
| `namespace` | `str` | `"chengeta"` | Prefix applied to every cache key |
| `key_hash_algo` | `"sha256" \| "md5"` | `"sha256"` | Hash algorithm for key generation |

### TTL Configuration

| Field | Type | Default | Description |
|---|---|---|---|
| `default_ttl` | `int \| None` | `3600` | Default TTL in seconds; `None` disables expiry |
| `ttl_embedding` | `int \| None` | `86400` | TTL for embedding cache entries (24 hours) |
| `ttl_retrieval` | `int \| None` | `3600` | TTL for retrieval cache entries (1 hour) |
| `ttl_context` | `int \| None` | `1800` | TTL for context cache entries (30 minutes) |
| `ttl_response` | `int \| None` | `600` | TTL for response cache entries (10 minutes) |

### Semantic / Vector Configuration

| Field | Type | Default | Description |
|---|---|---|---|
| `semantic_threshold` | `float` | `0.95` | Minimum cosine similarity for a semantic cache hit |
| `vector_backend` | `"faiss" \| "chroma" \| "none"` | `"none"` | Vector similarity backend |
| `embedding_dim` | `int` | `1536` | Embedding vector dimension (used by FAISS backend) |

:::note
The `embedding_dim` default of 1536 matches OpenAI's `text-embedding-3-small` model. Adjust this to match your embedding model's output dimension.
:::


---

## Environment Variable Reference

Every field maps to an `CHENGETA_*` environment variable. The `from_env()` classmethod handles type conversion automatically.

| Variable | Type | Default | Maps to |
|---|---|---|---|
| `CHENGETA_BACKEND` | `str` | `memory` | `backend` |
| `CHENGETA_REDIS_URL` | `str` | `redis://localhost:6379/0` | `redis_url` |
| `CHENGETA_DISK_PATH` | `str` | `/tmp/chengeta` | `disk_path` |
| `CHENGETA_DEFAULT_TTL` | `int \| "none"` | `3600` | `default_ttl` |
| `CHENGETA_SEMANTIC_THRESHOLD` | `float` | `0.95` | `semantic_threshold` |
| `CHENGETA_VECTOR_BACKEND` | `str` | `none` | `vector_backend` |
| `CHENGETA_EMBEDDING_DIM` | `int` | `1536` | `embedding_dim` |
| `CHENGETA_MAX_MEMORY_ENTRIES` | `int` | `10000` | `max_memory_entries` |
| `CHENGETA_KEY_HASH_ALGO` | `str` | `sha256` | `key_hash_algo` |
| `CHENGETA_NAMESPACE` | `str` | `chengeta` | `namespace` |
| `CHENGETA_TTL_EMBEDDING` | `int \| "none"` | `86400` | `ttl_embedding` |
| `CHENGETA_TTL_RETRIEVAL` | `int \| "none"` | `3600` | `ttl_retrieval` |
| `CHENGETA_TTL_CONTEXT` | `int \| "none"` | `1800` | `ttl_context` |
| `CHENGETA_TTL_RESPONSE` | `int \| "none"` | `600` | `ttl_response` |

:::tip[Disabling TTL via environment]
Set any TTL variable to the string `"none"` (case-insensitive) to disable expiry for that cache type:

```bash
export CHENGETA_TTL_EMBEDDING=none
```
:::


---

## API Reference

### Constructor

```python
@dataclass
class ChengetaSettings:
    backend: Literal["memory", "redis", "disk"] = "memory"
    redis_url: str = "redis://localhost:6379/0"
    disk_path: str = "/tmp/chengeta"
    default_ttl: int | None = 3600
    semantic_threshold: float = 0.95
    vector_backend: Literal["faiss", "chroma", "none"] = "none"
    embedding_dim: int = 1536
    max_memory_entries: int = 10_000
    key_hash_algo: Literal["sha256", "md5"] = "sha256"
    namespace: str = "chengeta"
    ttl_embedding: int | None = 86400
    ttl_retrieval: int | None = 3600
    ttl_context: int | None = 1800
    ttl_response: int | None = 600
```

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `from_env` | `from_env()` | `ChengetaSettings` | Classmethod: build settings from `CHENGETA_*` environment variables |

---

### Method Details

#### `from_env()`

Build an `ChengetaSettings` instance by reading `CHENGETA_*` environment variables. Any variable not set falls back to the field's default value. Integer fields are parsed with `int()`, float fields with `float()`, and TTL fields accept the string `"none"` to represent `None`.

```python
import os
os.environ["CHENGETA_BACKEND"] = "disk"
os.environ["CHENGETA_DISK_PATH"] = "/data/cache"
os.environ["CHENGETA_DEFAULT_TTL"] = "7200"

settings = ChengetaSettings.from_env()
print(settings.backend)      # "disk"
print(settings.disk_path)    # "/data/cache"
print(settings.default_ttl)  # 7200
```

---

## Example Configurations

### Development (In-Memory)

```python
settings = ChengetaSettings(
    backend="memory",
    max_memory_entries=1000,
    default_ttl=60,
    namespace="dev",
)
```

### Production (Redis + FAISS)

```python
settings = ChengetaSettings(
    backend="redis",
    redis_url="redis://cache.internal:6379/0",
    namespace="prod",
    default_ttl=3600,
    ttl_response=300,
    vector_backend="faiss",
    embedding_dim=1536,
    semantic_threshold=0.93,
    key_hash_algo="sha256",
)
```

### Disk-Based (Serverless / Edge)

```python
settings = ChengetaSettings(
    backend="disk",
    disk_path="/tmp/chengeta",
    default_ttl=1800,
    vector_backend="none",
)
```

:::warning
When using `backend="redis"`, ensure the Redis server is reachable at the configured `redis_url`. The `CacheManager.from_settings()` factory will attempt to connect immediately.
:::


---

## Next Steps

- [CacheManager](cache-manager.md) -- Pass settings to `CacheManager.from_settings()`
- [Policies](policies.md) -- How TTL settings become a `TTLPolicy`
- [Configuration Guide](../getting-started/configuration.md) -- Overview of all configuration options
