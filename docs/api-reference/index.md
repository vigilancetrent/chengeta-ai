# API Reference

Complete class and method reference for every module in chengeta-ai.

---

## Core

### `CacheManager`

::: chengeta_ai.core.cache_manager

The central orchestrator that wires together backends, key builder, TTL policies, and invalidation.

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
```

| Method | Signature | Returns | Description |
|---|---|---|---|
| `__init__` | `(backend, key_builder, ttl_policy=None, vector_backend=None, invalidation_engine=None, semantic_threshold=0.95)` | — | Create a new manager |
| `get` | `(key, semantic=False, vector=None)` | `Any \| None` | Retrieve cached value (exact or semantic) |
| `set` | `(key, value, ttl=None, vector=None, tags=None, cache_type="response")` | `None` | Store a value |
| `delete` | `(key)` | `None` | Remove a key |
| `exists` | `(key)` | `bool` | Check if key exists |
| `invalidate` | `(tag)` | `int` | Remove all keys with tag |
| `clear` | `()` | `None` | Flush all entries |
| `close` | `()` | `None` | Release resources |
| `from_settings` | `(settings)` | `CacheManager` | Factory from ChengetaSettings |

**Properties:** `key_builder`, `ttl_policy`

---

### `CacheKeyBuilder`

```python
from chengeta_ai import CacheKeyBuilder
```

| Method | Signature | Returns | Description |
|---|---|---|---|
| `__init__` | `(namespace="chengeta", algo="sha256")` | — | Create key builder |
| `build` | `(cache_type, content, extra=None)` | `str` | Build a cache key |

**Key format:** `{namespace}:{type_prefix}:{hash[:16]}`

**Type prefixes:** `embedding` -> `embed`, `retrieval` -> `retrieval`, `context` -> `ctx`, `response` -> `resp`

---

### `TTLPolicy`

```python
from chengeta_ai import TTLPolicy
```

| Field | Type | Default | Description |
|---|---|---|---|
| `default_ttl` | `int \| None` | `3600` | Fallback TTL in seconds |
| `per_type` | `dict[str, int \| None]` | `{}` | Per-cache-type overrides |

| Method | Signature | Returns |
|---|---|---|
| `ttl_for` | `(cache_type)` | `int \| None` |
| `from_settings` | `(settings)` | `TTLPolicy` |

---

### `EvictionPolicy`

```python
from chengeta_ai import EvictionPolicy
```

| Field | Type | Default |
|---|---|---|
| `strategy` | `"lru" \| "ttl_only"` | `"lru"` |
| `max_entries` | `int \| None` | `None` |
| `max_bytes` | `int \| None` | `None` |

---

### `InvalidationEngine`

```python
from chengeta_ai.core.invalidation import InvalidationEngine
```

| Method | Signature | Returns | Description |
|---|---|---|---|
| `__init__` | `(tag_store)` | — | Create with a backend for tag storage |
| `register` | `(key, tags)` | `None` | Associate key with tags |
| `invalidate_tag` | `(tag, backend)` | `int` | Remove all keys for a tag |
| `invalidate_key` | `(key, backend)` | `None` | Remove a specific key |

---

### `ChengetaSettings`

```python
from chengeta_ai import ChengetaSettings
```

| Field | Type | Default |
|---|---|---|
| `backend` | `"memory" \| "disk" \| "redis"` | `"memory"` |
| `redis_url` | `str` | `"redis://localhost:6379/0"` |
| `disk_path` | `str` | `"/tmp/chengeta"` |
| `default_ttl` | `int \| None` | `3600` |
| `semantic_threshold` | `float` | `0.95` |
| `vector_backend` | `"faiss" \| "chroma" \| "none"` | `"none"` |
| `embedding_dim` | `int` | `1536` |
| `max_memory_entries` | `int` | `10000` |
| `key_hash_algo` | `"sha256" \| "md5"` | `"sha256"` |
| `namespace` | `str` | `"chengeta"` |
| `ttl_embedding` | `int \| None` | `86400` |
| `ttl_retrieval` | `int \| None` | `3600` |
| `ttl_context` | `int \| None` | `1800` |
| `ttl_response` | `int \| None` | `600` |

| Method | Returns |
|---|---|
| `from_env()` | `ChengetaSettings` |

---

## Backends

### `CacheBackend` (Protocol)

```python
from chengeta_ai.backends.base import CacheBackend
```

| Method | Signature | Returns |
|---|---|---|
| `get` | `(key: str)` | `Any \| None` |
| `set` | `(key: str, value: Any, ttl: int \| None = None)` | `None` |
| `delete` | `(key: str)` | `None` |
| `exists` | `(key: str)` | `bool` |
| `clear` | `()` | `None` |
| `close` | `()` | `None` |

### `VectorBackend` (Protocol)

```python
from chengeta_ai.backends.base import VectorBackend
```

| Method | Signature | Returns |
|---|---|---|
| `add` | `(key, vector, metadata)` | `None` |
| `search` | `(vector, top_k=1)` | `list[tuple[str, float]]` |
| `delete` | `(key)` | `None` |
| `clear` | `()` | `None` |
| `close` | `()` | `None` |

### `InMemoryBackend`

```python
from chengeta_ai import InMemoryBackend
```

`__init__(max_size: int = 10_000)` — Thread-safe LRU cache with TTL support.

### `DiskBackend`

```python
from chengeta_ai import DiskBackend
```

`__init__(directory: str, size_limit: int = 2**30)` — Persistent cache via diskcache.

### `RedisBackend`

```python
from chengeta_ai.backends.redis_backend import RedisBackend
```

`__init__(url: str = "redis://localhost:6379/0", key_prefix: str = "")` — Requires `pip install 'chengeta-ai[redis]'`.

### `FAISSBackend`

```python
from chengeta_ai.backends.vector_backend import FAISSBackend
```

`__init__(dim: int, normalize: bool = True)` — Requires `pip install 'chengeta-ai[vector-faiss]'`.

### `ChromaBackend`

```python
from chengeta_ai.backends.vector_backend import ChromaBackend
```

`__init__(collection_name: str = "chengeta", persist_directory: str | None = None)` — Requires `pip install 'chengeta-ai[vector-chroma]'`.

---

## Cache Layers

### `ResponseCache`

```python
from chengeta_ai.layers.response_cache import ResponseCache
```

| Method | Signature | Returns |
|---|---|---|
| `__init__` | `(manager)` | — |
| `get` | `(messages, model_id="default", params=None)` | `Any \| None` |
| `set` | `(messages, response, model_id="default", params=None, ttl=None, tags=None)` | `None` |
| `get_or_generate` | `(messages, generate_fn, model_id, params, ttl)` | `Any` |
| `invalidate_model` | `(model_id)` | `int` |

### `EmbeddingCache`

```python
from chengeta_ai.layers.embedding_cache import EmbeddingCache
```

| Method | Signature | Returns |
|---|---|---|
| `__init__` | `(manager, dim=1536)` | — |
| `get` | `(text, model_id="default")` | `np.ndarray \| None` |
| `set` | `(text, vector, model_id="default", ttl=None)` | `None` |
| `get_or_compute` | `(text, compute_fn, model_id, ttl)` | `np.ndarray` |

### `RetrievalCache`

```python
from chengeta_ai.layers.retrieval_cache import RetrievalCache
```

| Method | Signature | Returns |
|---|---|---|
| `__init__` | `(manager)` | — |
| `get` | `(query, retriever_id="default", top_k=5)` | `list \| None` |
| `set` | `(query, documents, retriever_id="default", top_k=5, ttl=None, tags=None)` | `None` |
| `get_or_retrieve` | `(query, retrieve_fn, retriever_id, top_k, ttl)` | `list` |

### `ContextCache`

```python
from chengeta_ai.layers.context_cache import ContextCache
```

| Method | Signature | Returns |
|---|---|---|
| `__init__` | `(manager)` | — |
| `get` | `(session_id, turn_index=None)` | `list \| None` |
| `set` | `(session_id, messages, turn_index=None, ttl=None, tags=None)` | `None` |
| `invalidate_session` | `(session_id)` | `int` |

### `SemanticCache`

```python
from chengeta_ai.layers.semantic_cache import SemanticCache
```

| Method | Signature | Returns |
|---|---|---|
| `__init__` | `(exact_backend, vector_backend, embed_fn, threshold=0.95, key_builder=None)` | — |
| `get` | `(query)` | `Any \| None` |
| `set` | `(query, value, ttl=None)` | `None` |
| `delete` | `(query)` | `None` |
| `clear` | `()` | `None` |

---

## Middleware

### `LLMMiddleware`

```python
from chengeta_ai.middleware.llm_middleware import LLMMiddleware
```

`__init__(response_cache, key_builder, model_id="default")` — Wraps sync LLM callables. Use as `@middleware` decorator.

### `AsyncLLMMiddleware`

```python
from chengeta_ai.middleware.llm_middleware import AsyncLLMMiddleware
```

`__init__(response_cache, key_builder, model_id="default")` — Auto-detects sync/async callables.

### `EmbeddingMiddleware`

```python
from chengeta_ai.middleware.embedding_middleware import EmbeddingMiddleware
```

`__init__(embedding_cache, model_id="default")` — Wraps sync/async embedding functions.

### `RetrieverMiddleware`

```python
from chengeta_ai.middleware.retriever_middleware import RetrieverMiddleware
```

`__init__(retrieval_cache, retriever_id="default", default_top_k=5)` — Wraps sync/async retriever functions.

---

## Adapters

### `LangChainCacheAdapter`

```python
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
```

`__init__(manager)` — Implements `langchain_core.caches.BaseCache`. Methods: `lookup`, `update`, `alookup`, `aupdate`, `clear`.

### `LangGraphCacheAdapter`

```python
from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter
```

`__init__(cache_manager)` — Implements `BaseCheckpointSaver` for both langgraph 0.x and 1.x. Methods: `get`, `get_tuple`, `put`, `put_writes`, `list`, `aget_tuple`, `aput`, `aput_writes`, `alist`, `get_next_version`.

### `AutoGenCacheAdapter`

```python
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter
```

`__init__(agent, cache_manager)` — Supports both `autogen-agentchat 0.4+` and `pyautogen 0.2.x`. Methods: `generate_reply`, `run`, `arun`.

### `CrewAICacheAdapter`

```python
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter
```

`__init__(crew, cache_manager)` — Wraps `Crew.kickoff()`. Methods: `kickoff`, `kickoff_async`.

### `AgnoCacheAdapter`

```python
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter
```

`__init__(agent, cache_manager)` — Wraps Agno `Agent.run()`. Methods: `run`, `arun`.

### `A2ACacheAdapter`

```python
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter
```

`__init__(cache_manager, agent_id="default")` — Caches A2A task results. Methods: `process`, `aprocess`, `wrap`.
