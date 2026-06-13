---
title: "ChromaBackend"
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ChromaBackend

A vector similarity backend powered by [ChromaDB](https://www.trychroma.com/). Supports both ephemeral (in-memory) and persistent (on-disk) modes with native HNSW-based cosine similarity search and metadata filtering.

## Overview

`ChromaBackend` wraps ChromaDB's collection API to provide vector storage and similarity search. Unlike `FAISSBackend`, it handles persistence natively and stores metadata alongside vectors, making it suitable for production deployments where durability matters.

**When to use it:**

- Production semantic cache layers that need persistence across restarts
- Applications that benefit from metadata filtering on search results
- Deployments where you want a managed vector store without running a separate service
- Workloads requiring native deletion and upsert semantics

**Tradeoffs:**

- Heavier dependency than FAISS (pulls in more packages).
- HNSW index provides approximate nearest neighbors (not exact like FAISS IndexFlat).
- Slightly higher per-query latency compared to in-memory FAISS for small collections.
- ChromaDB manages its own storage format -- less control over internals.

## Installation

`chromadb` is an optional dependency. Install it with the `vector-chroma` extra:

<Tabs>
<TabItem value="pip" label="pip">

```bash
pip install 'chengeta-ai[vector-chroma]'
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="uv" label="uv">

```bash
uv add 'chengeta-ai[vector-chroma]'
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="poetry" label="poetry">

```bash
poetry add chengeta-ai -E vector-chroma
```

</TabItem>

</Tabs>


:::warning[Import guard]
If `chromadb` is not installed, instantiating `ChromaBackend` raises an
`ImportError` with installation instructions.
:::


## Usage

### Ephemeral mode (in-memory)

```python
import numpy as np
from chengeta_ai.backends.vector_backend import ChromaBackend

# No persist_directory = EphemeralClient (data lost on exit)
backend = ChromaBackend(collection_name="my_cache")

embedding = np.random.randn(384).astype(np.float32)
backend.add("doc:1", embedding, metadata={"value": "document content", "source": "wiki"})

results = backend.search(embedding, top_k=3)
for key, score in results:
    print(f"{key}: {score:.4f}")
```

### Persistent mode (on-disk)

```python
from chengeta_ai.backends.vector_backend import ChromaBackend

# Data persisted to disk -- survives process restarts
backend = ChromaBackend(
    collection_name="semantic_cache",
    persist_directory="/var/data/chroma",
)

# Add vectors across sessions
backend.add("query:abc", query_embedding, metadata={"value": "cached answer"})

# After restart, the same data is available
backend = ChromaBackend(
    collection_name="semantic_cache",
    persist_directory="/var/data/chroma",
)
results = backend.search(query_embedding, top_k=1)
# [("query:abc", 0.9998)]
```

### Retrieving stored values

```python
backend.add("prompt:xyz", embedding, metadata={"value": "LLM response text"})

# Retrieve the stored value by key
cached = backend.get_value("prompt:xyz")  # "LLM response text"
```

### Multiple collections

```python
# Separate collections for different data types
response_cache = ChromaBackend(collection_name="responses", persist_directory="./chroma")
embedding_cache = ChromaBackend(collection_name="embeddings", persist_directory="./chroma")
```

:::tip[Upsert semantics]
`ChromaBackend.add()` uses Chroma's `upsert` operation. If a key already
exists, its vector and metadata are updated in place -- no need to
delete before re-adding.
:::


:::note[Cosine similarity scores]
ChromaDB returns cosine **distances** (lower = more similar). The backend
converts these to similarity scores using `similarity = 1.0 - distance`,
so scores range from 0.0 (completely dissimilar) to 1.0 (identical).
:::


:::note[Metadata serialization]
All metadata values are converted to strings before storage
(`str(v)` for each value). Keep this in mind when storing numeric or
complex metadata -- you will receive string representations back from
`get_value()`.
:::


:::warning[HNSW approximation]
ChromaDB uses an HNSW index for search, which provides approximate
nearest neighbors. For very small collections, results are effectively
exact. For large collections, there is a small chance that the true
nearest neighbor is missed.
:::


## API Reference

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `collection_name` | `str` | `"chengeta"` | Name of the ChromaDB collection to use. Created automatically if it does not exist (`get_or_create_collection`). |
| `persist_directory` | `str \| None` | `None` | If set, data is persisted to this directory using `PersistentClient`. If `None`, an `EphemeralClient` is used and data lives only in memory. |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `add` | `add(key: str, vector: np.ndarray, metadata: dict[str, Any])` | `None` | Upsert a vector with metadata into the collection. The vector is converted to `float32` and stored as a list. Metadata values are stringified. |
| `search` | `search(vector: np.ndarray, top_k: int = 1)` | `list[tuple[str, float]]` | Return the `top_k` nearest neighbors as `(key, similarity_score)` tuples. Scores are cosine similarities (`1.0 - distance`). |
| `get_value` | `get_value(key: str)` | `Any \| None` | Return the `"value"` field from the stored metadata for the given key, or `None` if the key does not exist. |
| `delete` | `delete(key: str)` | `None` | Remove the vector and its metadata from the collection by ID. |
| `clear` | `clear()` | `None` | Remove all entries from the collection. |
| `close` | `close()` | `None` | No-op. ChromaDB manages its own resources. Included for protocol compatibility. |
