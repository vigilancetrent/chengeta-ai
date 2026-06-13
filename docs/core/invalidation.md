# InvalidationEngine

The `InvalidationEngine` provides tag-based cache invalidation: associate keys with tags, then invalidate all keys sharing a tag in a single operation.

---

## Overview

TTL-based expiration handles routine staleness, but sometimes you need to invalidate cache entries immediately -- when a model is updated, a user's data changes, or a document is re-indexed. The `InvalidationEngine` solves this by letting you associate cache keys with arbitrary string tags and then bulk-remove all keys for a given tag.

The engine maintains a separate tag-to-key mapping in its own `CacheBackend` (typically an `InMemoryBackend`), keeping the tag index isolated from the primary cache namespace. This design means:

- Tag metadata does not pollute the primary cache.
- The tag store can use a different backend or TTL than the primary store.
- Tag lookups are fast key-value reads, not scans.

---

## Usage

### Standalone Usage

```python
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.core.invalidation import InvalidationEngine

# Create a tag store and the engine
tag_store = InMemoryBackend()
engine = InvalidationEngine(tag_store=tag_store)

# Create a primary cache backend
cache = InMemoryBackend()

# Store some values in the primary cache
cache.set("resp:a1b2", "Answer about Python")
cache.set("resp:c3d4", "Answer about Java")
cache.set("resp:e5f6", "Answer about Rust")

# Register tags
engine.register("resp:a1b2", ["lang:python", "model:gpt-4"])
engine.register("resp:c3d4", ["lang:java", "model:gpt-4"])
engine.register("resp:e5f6", ["lang:rust", "model:claude-3"])
```

### Invalidating by Tag

```python
# Remove all entries tagged "model:gpt-4"
removed = engine.invalidate_tag("model:gpt-4", backend=cache)
print(f"Removed {removed} keys")  # 2

# Verify
print(cache.exists("resp:a1b2"))  # False
print(cache.exists("resp:c3d4"))  # False
print(cache.exists("resp:e5f6"))  # True (different tag)
```

### Invalidating a Single Key

```python
# Remove one specific key
engine.invalidate_key("resp:e5f6", backend=cache)
print(cache.exists("resp:e5f6"))  # False
```

### Through CacheManager

In practice, you rarely use `InvalidationEngine` directly. The `CacheManager` exposes tag registration via `set()` and invalidation via `invalidate()`:

```python
from chengeta_ai import CacheManager, ChengetaSettings

manager = CacheManager.from_settings(ChengetaSettings())

# Tags are registered automatically during set()
manager.set("key1", "value1", tags=["user:alice", "session:xyz"])
manager.set("key2", "value2", tags=["user:alice", "session:abc"])
manager.set("key3", "value3", tags=["user:bob", "session:xyz"])

# Invalidate all of Alice's cached data
removed = manager.invalidate("user:alice")
print(f"Removed {removed} entries")  # 2
```

!!! tip "Common tagging patterns"
    Use structured tags to organize your invalidation strategy:

    - `user:{id}` -- Invalidate when user data changes
    - `model:{name}` -- Invalidate when switching or updating models
    - `doc:{id}` -- Invalidate when a source document is updated
    - `session:{id}` -- Clear session-scoped caches
    - `version:{n}` -- Invalidate across version bumps

---

## How It Works

The engine stores tag-to-key mappings as JSON arrays in the tag store under keys prefixed with `__tag__:`.

```
__tag__:model:gpt-4  -->  ["resp:a1b2", "resp:c3d4"]
__tag__:user:alice    -->  ["key1", "key2"]
```

When `register()` is called:

1. The engine reads the existing key list for each tag.
2. Appends the new key if it is not already present.
3. Writes the updated list back to the tag store.

When `invalidate_tag()` is called:

1. The engine reads the key list for the tag.
2. Deletes each key from the primary cache backend.
3. Removes the tag entry from the tag store.
4. Returns the count of deleted keys.

!!! note
    The `invalidate_key()` method only deletes the key from the primary backend. It does not remove the key from any tag mappings. This is a lightweight operation for cases where you know the exact key to remove.

---

## API Reference

### Constructor

```python
InvalidationEngine(tag_store: CacheBackend)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `tag_store` | `CacheBackend` | *required* | Backend used to persist tag-to-key mappings |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `register` | `register(key, tags)` | `None` | Associate a cache key with one or more tags |
| `invalidate_tag` | `invalidate_tag(tag, backend)` | `int` | Remove all keys registered under a tag |
| `invalidate_key` | `invalidate_key(key, backend)` | `None` | Remove a specific key from the primary backend |

---

### Method Details

#### `register(key, tags)`

Associate a cache key with one or more string tags. If the key is already registered under a tag, it is not duplicated.

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` | The cache key to register |
| `tags` | `list[str]` | List of tags to associate with the key |

```python
engine.register("resp:abc123", ["user:alice", "model:gpt-4", "topic:science"])
```

!!! warning
    Tags are additive. Calling `register()` multiple times for the same key with different tags adds to the set of tags; it does not replace them.

---

#### `invalidate_tag(tag, backend)`

Remove all cache keys that were registered under the given tag. Deletes the keys from the primary backend and cleans up the tag mapping.

| Parameter | Type | Description |
|---|---|---|
| `tag` | `str` | The tag to invalidate |
| `backend` | `CacheBackend` | The primary cache backend to delete keys from |

**Returns:** `int` -- the number of keys removed.

```python
removed = engine.invalidate_tag("model:gpt-4", backend=cache)
```

!!! note
    If the tag does not exist or has no associated keys, the method returns `0` without error.

---

#### `invalidate_key(key, backend)`

Remove a specific key from the primary backend. This is a convenience method that delegates to `backend.delete(key)`.

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` | The cache key to remove |
| `backend` | `CacheBackend` | The primary cache backend |

```python
engine.invalidate_key("resp:abc123", backend=cache)
```

---

## Next Steps

- [CacheManager](cache-manager.md) -- Exposes invalidation through `set(tags=...)` and `invalidate(tag)`
- [Policies](policies.md) -- TTL-based expiration as a complement to manual invalidation
- [Settings](settings.md) -- Configure the system via environment variables
