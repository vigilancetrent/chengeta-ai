# EmbeddingCache

Cache dense vector embeddings so the same text is never embedded twice.

---

## Overview

`EmbeddingCache` stores `numpy.ndarray` vectors produced by embedding models (OpenAI, Cohere, sentence-transformers, etc.). Vectors are keyed by:

- **text** -- the input string that was embedded.
- **model ID** -- distinguishes embeddings from different models or model versions.

Serialization uses numpy's native `tobytes()` / `frombuffer()` for zero-copy efficiency rather than pickle. The dimension must be known at construction time so that raw bytes can be reshaped on read.

**When to use:** Any pipeline that embeds text -- RAG ingestion, semantic search, clustering, classification with embeddings. Embedding API calls are billed per token; caching eliminates redundant spend entirely.

!!! note "Dimension must match"
    The `dim` parameter must match the output dimension of your embedding model. OpenAI `text-embedding-3-small` produces 1536-dimensional vectors by default; other models differ.

---

## Usage

### Basic get / set

```python
import numpy as np
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.layers.embedding_cache import EmbeddingCache

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
)
cache = EmbeddingCache(manager, dim=1536)

text = "The quick brown fox jumps over the lazy dog."
vector = np.random.rand(1536).astype(np.float32)  # pretend this came from an API

# Store
cache.set(text, vector, model_id="text-embedding-3-small")

# Retrieve
cached = cache.get(text, model_id="text-embedding-3-small")
print(cached.shape)  # (1536,)
print(np.allclose(cached, vector))  # True
```

### get_or_compute -- embed on miss

```python
def embed(text: str) -> np.ndarray:
    response = openai.embeddings.create(
        model="text-embedding-3-small", input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# Cached if available; otherwise calls embed(), stores, and returns.
vector = cache.get_or_compute(
    text="What is machine learning?",
    compute_fn=embed,
    model_id="text-embedding-3-small",
    ttl=86400,
)
```

---

## How It Works

1. **Key construction** -- `CacheKeyBuilder.build("embedding", text, extra={"model": model_id})` produces a key like `chengeta:embed:7c3a1f9e0b2d4a56`.
2. **Serialization (write)** -- The numpy array is cast to `float32` and serialized with `vector.astype(np.float32).tobytes()`, producing a compact byte string of `dim * 4` bytes.
3. **Deserialization (read)** -- Raw bytes are reconstructed with `np.frombuffer(raw, dtype=np.float32).copy()`. The `.copy()` ensures the returned array owns its memory and is safely mutable.
4. **Storage** -- Bytes are passed to `CacheManager.set()` with `cache_type="embedding"` so the TTL policy can apply embedding-specific defaults.

```
"What is ML?"  +  model_id="text-embedding-3-small"
       |
       v
  CacheKeyBuilder.build("embedding", text, extra={"model": ...})
       |
       v
  "chengeta:embed:7c3a1f9e0b2d4a56"
       |
       v
  Backend stores: key -> vector.tobytes()  (6144 bytes for dim=1536)
```

!!! tip "Memory efficiency"
    A 1536-dim float32 vector is only 6 KB as raw bytes. Pickle would add object headers and metadata overhead. The `tobytes` approach is both smaller and faster.

---

## API Reference

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `manager` | `CacheManager` | *required* | The underlying cache manager instance. |
| `dim` | `int` | `1536` | Embedding dimension. Must match the model output size. |

### Methods

| Method | Parameters | Returns | Description |
|---|---|---|---|
| `get` | `text: str`, `model_id: str = "default"` | `np.ndarray \| None` | Retrieve a cached embedding vector, or `None` on miss. |
| `set` | `text: str`, `vector: np.ndarray`, `model_id: str = "default"`, `ttl: int \| None = None` | `None` | Store an embedding vector in the cache. |
| `get_or_compute` | `text: str`, `compute_fn: Callable[[str], np.ndarray]`, `model_id: str = "default"`, `ttl: int \| None = None` | `np.ndarray` | Return cached embedding or call `compute_fn`, cache, and return the result. |

---

## Source

:material-file-code: `chengeta_ai/layers/embedding_cache.py`
