---
title: "FAISSBackend"
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# FAISSBackend

A high-performance in-memory vector similarity backend powered by [FAISS](https://github.com/facebookresearch/faiss). Uses `IndexFlatIP` (inner product) on L2-normalized vectors to compute cosine similarity.

## Overview

`FAISSBackend` wraps Facebook AI Similarity Search (FAISS) to provide exact nearest-neighbor lookup over dense embedding vectors. It stores vectors in a flat index with brute-force search, which is fast for small-to-medium collections (up to a few million vectors) and guarantees exact results.

**When to use it:**

- Semantic cache layers that need fast cosine-similarity search
- In-process vector lookups without external infrastructure
- Prototyping and development of similarity-based features
- Workloads where exact (not approximate) nearest-neighbor results matter

**Tradeoffs:**

- In-memory only -- all data is lost on process exit.
- Search is brute-force O(n), so it slows down with very large collections.
- Deletion is soft (key mappings are removed, but the vector remains in the FAISS index until `clear()` is called).
- No built-in metadata filtering -- filter results after search if needed.

## Installation

`faiss-cpu` is an optional dependency. Install it with the `vector-faiss` extra:

<Tabs>
<TabItem value="pip" label="pip">

```bash
pip install 'chengeta-ai[vector-faiss]'
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="uv" label="uv">

```bash
uv add 'chengeta-ai[vector-faiss]'
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="poetry" label="poetry">

```bash
poetry add chengeta-ai -E vector-faiss
```

</TabItem>

</Tabs>


:::warning[Import guard]
If `faiss-cpu` is not installed, instantiating `FAISSBackend` raises an
`ImportError` with installation instructions.
:::


## Usage

### Basic vector similarity search

```python
import numpy as np
from chengeta_ai.backends.vector_backend import FAISSBackend

# Create a backend for 384-dimensional embeddings
backend = FAISSBackend(dim=384, normalize=True)

# Add vectors with metadata
embedding_a = np.random.randn(384).astype(np.float32)
embedding_b = np.random.randn(384).astype(np.float32)

backend.add("doc:1", embedding_a, metadata={"value": "First document content"})
backend.add("doc:2", embedding_b, metadata={"value": "Second document content"})

# Search for the most similar vector
query = np.random.randn(384).astype(np.float32)
results = backend.search(query, top_k=5)
# [(key, similarity_score), ...]

for key, score in results:
    print(f"{key}: {score:.4f}")
```

### Retrieving stored values

```python
backend.add("prompt:abc", embedding, metadata={"value": "cached response"})

# Later, after a similarity search finds "prompt:abc":
cached = backend.get_value("prompt:abc")  # "cached response"
```

### Using with the semantic cache layer

```python
from chengeta_ai.backends.vector_backend import FAISSBackend

vector_backend = FAISSBackend(dim=1536, normalize=True)

# The semantic cache layer uses this backend internally to find
# semantically similar queries and return cached responses.
```

### Normalization behavior

<Tabs>
<TabItem value="normalize-true-default-" label="normalize=True (default)">

```python
# Vectors are L2-normalized before indexing and searching.
# Inner product on normalized vectors equals cosine similarity.
backend = FAISSBackend(dim=128, normalize=True)
# Scores range from -1.0 to 1.0 (cosine similarity)
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="normalize-false" label="normalize=False">

```python
# Vectors are used as-is. Inner product scores are unbounded.
# Use this only if your vectors are already normalized.
backend = FAISSBackend(dim=128, normalize=False)
```

</TabItem>

</Tabs>


:::tip[Cosine similarity via inner product]
FAISS `IndexFlatIP` computes the inner product between vectors. When
`normalize=True`, all vectors are L2-normalized before indexing, which
makes the inner product equivalent to cosine similarity. This is the
recommended mode for embedding similarity.
:::


:::note[Soft deletion]
FAISS `IndexFlat` does not support in-place vector removal. When you call
`delete(key)`, the key-to-ID mapping is removed so the vector will not
appear in search results, but the vector data remains in the index. Call
`clear()` to fully reset the index and reclaim memory.
:::


:::warning[Not persistent]
All vectors are stored in process memory. If you need persistence, use
[ChromaBackend](chroma.md) with a `persist_directory`.
:::


## API Reference

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `dim` | `int` | *(required)* | Dimensionality of the embedding vectors (e.g., 384, 768, 1536). |
| `normalize` | `bool` | `True` | If `True`, L2-normalize all vectors before indexing and searching. Enables cosine similarity via inner product. |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add` | `add(key: str, vector: np.ndarray, metadata: dict[str, Any])` | `None` | Index a vector under the given key. If the key already exists, the old entry is deleted first (soft delete) and the new vector is appended. The `metadata["value"]` field is stored for later retrieval via `get_value()`. |
| `search` | `search(vector: np.ndarray, top_k: int = 1)` | `list[tuple[str, float]]` | Return the `top_k` nearest neighbors as `(key, similarity_score)` tuples, sorted by descending similarity. Returns an empty list if the index is empty. |
| `get_value` | `get_value(key: str)` | `Any \| None` | Return the `metadata["value"]` stored for the given key, or `None` if the key does not exist. |
| `delete` | `delete(key: str)` | `None` | Remove the key from internal mappings. The vector data remains in the FAISS index but will no longer appear in search results. |
| `clear` | `clear()` | `None` | Reset the FAISS index and clear all internal mappings. Reclaims all memory. |
| `close` | `close()` | `None` | Release resources. Calls `clear()` internally. |
