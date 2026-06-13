# CacheKeyBuilder

The `CacheKeyBuilder` generates deterministic, namespaced cache keys by hashing content into a canonical form. It guarantees that identical inputs always produce the same key, regardless of dictionary key ordering or serialization quirks.

---

## Overview

Cache key collisions can silently corrupt data; overly verbose keys waste memory. `CacheKeyBuilder` solves both problems with a structured key schema:

```
{namespace}:{type_prefix}:{hash[:16]}
```

For example: `chengeta:resp:a3f9b2c1d4e5f678`

The builder:

1. Maps the `cache_type` to a short prefix (e.g., `"response"` becomes `"resp"`).
2. Serializes the content and any extra discriminators into canonical JSON (sorted keys, ASCII-safe).
3. Hashes the JSON with SHA-256 (default) or MD5 and truncates to 16 hex characters.
4. Prepends the namespace and prefix.

This produces compact, collision-resistant keys that are human-readable enough for debugging.

---

## Usage

### Basic Key Generation

```python
from chengeta_ai.core.key_builder import CacheKeyBuilder

kb = CacheKeyBuilder(namespace="myapp")

# Build a response cache key
key = kb.build("response", "What is the capital of France?")
print(key)  # myapp:resp:7c2a1f3b9e4d6a80

# Build an embedding cache key
key = kb.build("embedding", "Hello world")
print(key)  # myapp:embed:1a2b3c4d5e6f7890
```

### With Extra Discriminators

Use the `extra` parameter to differentiate keys that share the same content but differ in context (e.g., different models or versions).

```python
key_gpt4 = kb.build("response", "Explain gravity", extra={"model": "gpt-4"})
key_claude = kb.build("response", "Explain gravity", extra={"model": "claude-3"})

# These produce different keys because the extra dict differs
assert key_gpt4 != key_claude
```

### With Complex Content

The builder handles any JSON-serializable content: strings, lists, dicts, numbers, and nested structures.

```python
# Dict content (key order does not matter -- canonical JSON sorts keys)
key1 = kb.build("response", {"role": "user", "content": "Hi"})
key2 = kb.build("response", {"content": "Hi", "role": "user"})
assert key1 == key2  # Identical keys regardless of dict order

# List of messages
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "What is 2+2?"},
]
key = kb.build("response", messages, extra={"model": "gpt-4"})
```

### Custom Namespace and Algorithm

```python
# Use MD5 for faster hashing (when collision resistance is less critical)
kb_fast = CacheKeyBuilder(namespace="dev", algo="md5")
key = kb_fast.build("context", {"session_id": "abc123"})
print(key)  # dev:ctx:9f8e7d6c5b4a3210
```

!!! tip "Choosing a hash algorithm"
    Use `sha256` (the default) for production workloads where collision resistance matters. Use `md5` in development or benchmarking scenarios where speed is prioritized over security.

---

## Type Prefixes

The builder maps standard cache types to short prefixes. Custom types are used as-is.

| Cache Type | Prefix | Typical Use |
|---|---|---|
| `"embedding"` | `embed` | Embedding vector caches |
| `"retrieval"` | `retrieval` | RAG retrieval result caches |
| `"context"` | `ctx` | Agent context / session caches |
| `"response"` | `resp` | LLM response caches |
| *(custom)* | *(as-is)* | Any user-defined cache type |

```python
# Standard types use short prefixes
kb.build("embedding", "text")   # chengeta:embed:...
kb.build("retrieval", "query")  # chengeta:retrieval:...
kb.build("context", "session")  # chengeta:ctx:...
kb.build("response", "prompt")  # chengeta:resp:...

# Custom types pass through unchanged
kb.build("tool_call", "data")   # chengeta:tool_call:...
```

---

## Key Determinism

The builder guarantees deterministic key generation through canonical JSON serialization:

- Dictionary keys are sorted alphabetically.
- Output is ASCII-safe (`ensure_ascii=True`).
- Non-serializable objects fall back to `str()` via `default=str`.

```python
# These all produce the same key:
kb.build("response", {"b": 2, "a": 1})
kb.build("response", {"a": 1, "b": 2})
```

!!! warning
    Floating-point precision can affect key determinism. If your content includes floats, consider rounding them before passing to `build()` to avoid subtle mismatches across platforms.

---

## API Reference

### Constructor

```python
CacheKeyBuilder(namespace: str = "chengeta", algo: str = "sha256")
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `namespace` | `str` | `"chengeta"` | Global prefix applied to every key |
| `algo` | `str` | `"sha256"` | Hash algorithm: `"sha256"` (secure) or `"md5"` (faster) |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `build` | `build(cache_type, content, extra=None)` | `str` | Build a deterministic cache key |

---

### Method Details

#### `build(cache_type, content, extra=None)`

Build a cache key for the given cache type and content.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `cache_type` | `str` | *required* | One of `"embedding"`, `"retrieval"`, `"context"`, `"response"`, or a custom string |
| `content` | `Any` | *required* | Primary cache input (text, list, dict, etc.) |
| `extra` | `dict[str, Any] \| None` | `None` | Additional discriminators (e.g., `model_id`, `index_version`) |

**Returns:** A string key like `"chengeta:embed:a3f9b2c1d4e5f678"`.

---

## Integration with CacheManager

The `CacheKeyBuilder` is typically accessed through `CacheManager.key_builder`:

```python
from chengeta_ai import CacheManager, ChengetaSettings

manager = CacheManager.from_settings(ChengetaSettings(namespace="prod"))

# Use the manager's key builder
key = manager.key_builder.build("response", {"prompt": "Hello"}, extra={"model": "gpt-4"})
manager.set(key, "Hi there!", cache_type="response")
```

---

## Next Steps

- [CacheManager](cache-manager.md) -- Uses the key builder for all cache operations
- [Policies](policies.md) -- TTL resolution by cache type
- [Settings](settings.md) -- Configure namespace and hash algorithm
