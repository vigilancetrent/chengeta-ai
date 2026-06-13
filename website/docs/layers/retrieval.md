---
title: "RetrievalCache"
---

# RetrievalCache

Cache retriever results so the same query never triggers a redundant vector search.

---

## Overview

`RetrievalCache` stores lists of documents (or document chunks) returned by a retriever, keyed by:

- **query** -- the search string sent to the retriever.
- **retriever ID** -- distinguishes results from different retriever instances or index versions.
- **top_k** -- the number of results requested. The same query with `top_k=5` and `top_k=10` produces separate cache entries.

The cache uses `pickle` for serialization, so any list of picklable objects can be stored -- plain dicts, LangChain `Document` objects, or custom dataclasses.

**When to use:** RAG pipelines where the document corpus changes infrequently. If your index is updated hourly, set a TTL that matches. If it is static, omit the TTL for indefinite caching.

:::warning[Stale results]
When the underlying document index is updated, cached retrieval results become stale. Use TTL or tag-based invalidation to keep results fresh.
:::


---

## Usage

### Basic get / set

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.layers.retrieval_cache import RetrievalCache

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
)
cache = RetrievalCache(manager)

query = "How does photosynthesis work?"
documents = [
    {"text": "Photosynthesis converts CO2...", "score": 0.95},
    {"text": "Chlorophyll absorbs light...", "score": 0.91},
]

# Store
cache.set(query, documents, retriever_id="biology-index", top_k=5, ttl=7200)

# Retrieve
cached = cache.get(query, retriever_id="biology-index", top_k=5)
print(len(cached))  # 2
```

### get_or_retrieve -- search on miss

```python
def search(query: str, top_k: int) -> list:
    return vector_store.similarity_search(query, k=top_k)

# Cached if available; otherwise calls search(), stores, and returns.
docs = cache.get_or_retrieve(
    query="How does photosynthesis work?",
    retrieve_fn=search,
    retriever_id="biology-index",
    top_k=5,
    ttl=7200,
)
```

### top_k matters

```python
# These are two different cache entries:
cache.set("query", docs_5, top_k=5)
cache.set("query", docs_10, top_k=10)

cache.get("query", top_k=5)   # returns docs_5
cache.get("query", top_k=10)  # returns docs_10
```

---

## How It Works

1. **Key construction** -- `CacheKeyBuilder.build("retrieval", query, extra={"retriever": retriever_id, "top_k": top_k})` produces a key like `chengeta:retrieval:b4e2f8a1c9d03567`.
2. **Serialization** -- Document lists are serialized with `pickle.dumps` on write and deserialized with `pickle.loads` on read.
3. **Storage** -- Pickled bytes are passed to `CacheManager.set()` with `cache_type="retrieval"`.
4. **Tagging** -- Custom tags can be provided via the `tags` parameter for group invalidation (e.g. `["index:biology-v2"]`).

```
"How does photosynthesis work?" + retriever="bio" + top_k=5
       |
       v
  CacheKeyBuilder.build("retrieval", query, extra={"retriever": "bio", "top_k": 5})
       |
       v
  "chengeta:retrieval:b4e2f8a1c9d03567"
       |
       v
  Backend stores: key -> pickle.dumps(documents)
```

:::tip[Invalidate on index rebuild]
Tag your entries when setting them, then invalidate by tag when the index is rebuilt:

```python
cache.set(query, docs, tags=["index:v1"])
# ... later, after index rebuild ...
manager.invalidate("index:v1")
```
:::


---

## API Reference

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `manager` | `CacheManager` | *required* | The underlying cache manager instance. |

### Methods

| Method | Parameters | Returns | Description |
|---|---|---|---|
| `get` | `query: str`, `retriever_id: str = "default"`, `top_k: int = 5` | `list \| None` | Return cached retrieval results, or `None` on miss. |
| `set` | `query: str`, `documents: list`, `retriever_id: str = "default"`, `top_k: int = 5`, `ttl: int \| None = None`, `tags: list[str] \| None = None` | `None` | Store retrieval results in the cache. |
| `get_or_retrieve` | `query: str`, `retrieve_fn: Callable[[str, int], list]`, `retriever_id: str = "default"`, `top_k: int = 5`, `ttl: int \| None = None` | `list` | Return cached documents or call `retrieve_fn(query, top_k)`, cache, and return the result. |

:::note[`retrieve_fn` signature]
The `retrieve_fn` callable must accept two positional arguments: `(query: str, top_k: int)`. This matches the signature of most retriever/search APIs.
:::


---

## Source

 `chengeta_ai/layers/retrieval_cache.py`
