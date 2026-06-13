# RedisBackend

A distributed key-value cache backed by a Redis server. Values are serialized with `pickle` and stored with optional TTL. Supports key prefixing for multi-tenant or namespaced deployments.

## Overview

`RedisBackend` connects to an external Redis server and implements the `CacheBackend` protocol. It is the right choice when you need a cache shared across multiple processes, containers, or machines.

**When to use it:**

- Distributed or multi-node deployments
- Microservice architectures where multiple services share cached data
- Production systems that need server-managed eviction policies (e.g., allkeys-lru)
- High-availability setups with Redis Sentinel or Redis Cluster

**Tradeoffs:**

- Requires a running Redis server (operational overhead).
- Network latency on every operation (typically sub-millisecond on LAN).
- Values are pickled -- only cache data you trust (see security warning below).

## Installation

`redis` is an optional dependency. Install it with the `redis` extra:

=== "pip"

    ```bash
    pip install 'chengeta-ai[redis]'
    ```

=== "uv"

    ```bash
    uv add 'chengeta-ai[redis]'
    ```

=== "poetry"

    ```bash
    poetry add chengeta-ai -E redis
    ```

!!! warning "Import guard"
    If the `redis` package is not installed, instantiating `RedisBackend` raises
    an `ImportError` with installation instructions. The rest of Chengeta AI
    continues to work without it.

## Usage

### Basic key-value caching

```python
from chengeta_ai.backends.redis_backend import RedisBackend

cache = RedisBackend(url="redis://localhost:6379/0")

# Store a value with a 10-minute TTL
cache.set("user:42:session", {"token": "abc123"}, ttl=600)

# Retrieve it
session = cache.get("user:42:session")  # {"token": "abc123"}

# Check existence
cache.exists("user:42:session")  # True

# Delete a single key
cache.delete("user:42:session")

# Close the connection when done
cache.close()
```

### Key prefixing for multi-tenancy

```python
# Tenant-isolated caches sharing the same Redis instance
tenant_a = RedisBackend(url="redis://localhost:6379/0", key_prefix="tenant_a:")
tenant_b = RedisBackend(url="redis://localhost:6379/0", key_prefix="tenant_b:")

tenant_a.set("config", {"theme": "dark"})
tenant_b.set("config", {"theme": "light"})

tenant_a.get("config")  # {"theme": "dark"}
tenant_b.get("config")  # {"theme": "light"}

# clear() only removes keys matching the prefix
tenant_a.clear()  # Deletes only "tenant_a:*" keys
```

### Using with CacheManager

```python
from chengeta_ai import CacheManager, CacheKeyBuilder
from chengeta_ai.backends.redis_backend import RedisBackend

manager = CacheManager(
    backend=RedisBackend(
        url="redis://redis.internal:6379/0",
        key_prefix="myapp:",
    ),
    key_builder=CacheKeyBuilder(namespace="prod"),
)

manager.set("llm:response:hash", b"cached output", ttl=3600)
```

### Connection URL formats

```python
# Standard TCP connection
cache = RedisBackend(url="redis://localhost:6379/0")

# With authentication
cache = RedisBackend(url="redis://:password@redis-host:6379/0")

# With username and password (Redis 6+)
cache = RedisBackend(url="redis://username:password@redis-host:6379/0")

# TLS connection
cache = RedisBackend(url="rediss://redis-host:6380/0")

# Unix socket
cache = RedisBackend(url="unix:///var/run/redis/redis.sock?db=0")
```

!!! warning "Pickle security"
    Values are serialized with `pickle`. Never connect to an untrusted Redis
    server or load data written by untrusted sources, as unpickling can execute
    arbitrary code.

!!! tip "Prefix-aware clear"
    When `key_prefix` is set, `clear()` deletes only keys matching
    `{prefix}*` using `KEYS` + `DELETE`. Without a prefix, it calls
    `FLUSHDB`, which removes **all** keys in the database -- use with care.

!!! note "No `__len__` method"
    Unlike `InMemoryBackend` and `DiskBackend`, `RedisBackend` does not
    implement `__len__`. Use `redis-cli DBSIZE` or the Redis `INFO` command
    to inspect key counts on the server.

## API Reference

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `url` | `str` | `"redis://localhost:6379/0"` | Redis connection URL. Supports `redis://`, `rediss://` (TLS), and `unix://` schemes. |
| `key_prefix` | `str` | `""` (empty) | String prepended to every key. Useful for namespacing or multi-tenant isolation. |

### Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `get` | `get(key: str)` | `Any \| None` | Retrieve and unpickle the value for `key` (with prefix applied). Returns `None` if the key does not exist or has expired. |
| `set` | `set(key: str, value: Any, ttl: int \| None = None)` | `None` | Pickle and store the value. `ttl` is in seconds, passed to Redis as the `EX` parameter. `None` means no expiry. |
| `delete` | `delete(key: str)` | `None` | Remove a key from Redis. No-op if the key does not exist. |
| `exists` | `exists(key: str)` | `bool` | Return `True` if the key exists in Redis (with prefix applied). |
| `clear` | `clear()` | `None` | If `key_prefix` is set, delete all keys matching `{prefix}*`. Otherwise, flush the entire database (`FLUSHDB`). |
| `close` | `close()` | `None` | Close the Redis connection. |
