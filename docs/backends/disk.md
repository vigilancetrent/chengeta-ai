# DiskBackend

A persistent, file-system-backed cache that wraps the `diskcache.Cache` library. Data survives process restarts and is safe for concurrent multi-process access via SQLite-level locking.

## Overview

`DiskBackend` stores cached entries on the local file system using the excellent [`diskcache`](https://grantjenks.com/docs/diskcache/) library. Under the hood, values are serialized and stored in a SQLite database with configurable size limits.

**When to use it:**

- Single-node production deployments that need cache persistence
- Workloads where cache warmup is expensive and should survive restarts
- Multi-process applications on the same machine (e.g., gunicorn workers)
- Caches that may exceed available RAM

**Tradeoffs:**

- Slower than `InMemoryBackend` (disk I/O), but typically still sub-millisecond.
- Not shared across machines -- use [RedisBackend](redis.md) for distributed caching.
- Requires disk space proportional to cache size.

## Installation

`diskcache` is a core dependency of Chengeta AI and is installed automatically.

```bash
pip install chengeta-ai
```

## Usage

### Basic key-value caching

```python
from chengeta_ai.backends.disk_backend import DiskBackend

cache = DiskBackend(directory="/tmp/chengeta", size_limit=2**30)

# Store a value with a 5-minute TTL
cache.set("embedding:doc42", [0.1, 0.2, 0.3], ttl=300)

# Retrieve it (even after process restart)
result = cache.get("embedding:doc42")  # [0.1, 0.2, 0.3]

# Check existence
cache.exists("embedding:doc42")  # True

# Delete a single key
cache.delete("embedding:doc42")

# Clear all entries
cache.clear()

# Close when done (releases file handles)
cache.close()
```

### Using with CacheManager

```python
from chengeta_ai import CacheManager, CacheKeyBuilder
from chengeta_ai.backends.disk_backend import DiskBackend

manager = CacheManager(
    backend=DiskBackend(directory="./cache_data"),
    key_builder=CacheKeyBuilder(namespace="prod"),
)

manager.set("llm:response:abc", b"cached llm output", ttl=3600)
result = manager.get("llm:response:abc")
```

### Multi-process safety

=== "Gunicorn workers"

    ```python
    # Each gunicorn worker can safely share the same cache directory.
    # SQLite locking ensures consistency.
    cache = DiskBackend(directory="/var/cache/chengeta")
    cache.set("shared_key", "all workers see this")
    ```

=== "Multiprocessing"

    ```python
    from multiprocessing import Process
    from chengeta_ai.backends.disk_backend import DiskBackend

    def worker(key, value):
        cache = DiskBackend(directory="/tmp/shared_cache")
        cache.set(key, value, ttl=60)
        cache.close()

    procs = [
        Process(target=worker, args=(f"key_{i}", f"value_{i}"))
        for i in range(4)
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    ```

!!! tip "Cache directory"
    The `directory` is created automatically if it does not exist. Choose a
    path on a fast local disk (SSD preferred) for best performance.

!!! warning "Size limit behavior"
    When the cache exceeds `size_limit`, diskcache begins evicting entries using
    an approximation of LRU. The limit is not enforced byte-for-byte -- brief
    overages are possible during concurrent writes.

!!! note "Serialization"
    `diskcache` handles serialization internally. It efficiently stores bytes,
    strings, and numbers directly, and pickles complex Python objects
    automatically.

## API Reference

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `directory` | `str` | *(required)* | Path to the cache directory. Created if it does not exist. |
| `size_limit` | `int` | `2**30` (1 GiB) | Maximum total cache size in bytes. |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `get` | `get(key: str)` | `Any \| None` | Return the cached value, or `None` if the key is missing or expired. |
| `set` | `set(key: str, value: Any, ttl: int \| None = None)` | `None` | Store a value. `ttl` is in seconds; `None` means no expiry. Passed to diskcache as the `expire` parameter. |
| `delete` | `delete(key: str)` | `None` | Remove a key. No-op if the key does not exist. |
| `exists` | `exists(key: str)` | `bool` | Return `True` if the key is present and not expired. Uses the `in` operator on the underlying diskcache. |
| `clear` | `clear()` | `None` | Remove all entries from the cache. |
| `close` | `close()` | `None` | Close the underlying diskcache and release file handles. Always call this when shutting down, or use a context manager pattern. |
| `__len__` | `len(cache)` | `int` | Return the number of entries currently stored. |
