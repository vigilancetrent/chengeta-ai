---
title: "Redis Backend"
---

# Redis Backend

Use Redis as a shared, distributed cache backend. All processes and workers
that connect to the same Redis instance share the same cache.

```bash
pip install 'chengeta-ai[redis]'
```

---

## 9.1 Shared cache across multiple processes

A drop-in replacement for `InMemoryBackend` that works across processes.

```python
from chengeta_ai import CacheManager, CacheKeyBuilder
from chengeta_ai.backends.redis_backend import RedisBackend

manager = CacheManager(
    backend=RedisBackend(url="redis://localhost:6379/0", key_prefix="myapp:"),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)

# Works identically to InMemoryBackend — but shared across processes
manager.set("my_key", {"result": 42}, ttl=300)
print(manager.get("my_key"))
```

:::tip
Use separate Redis database numbers (e.g., `/0`, `/1`, `/2`) or distinct `key_prefix`
values to isolate caches for different applications on the same Redis server.
:::


---

## 9.2 Redis + LangChain

All workers sharing the same Redis instance benefit from a single shared LLM cache.

```python
from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI
from chengeta_ai import CacheManager, CacheKeyBuilder
from chengeta_ai.backends.redis_backend import RedisBackend
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

manager = CacheManager(
    backend=RedisBackend(url="redis://localhost:6379/1"),
    key_builder=CacheKeyBuilder(namespace="lc"),
)
set_llm_cache(LangChainCacheAdapter(manager))

llm = ChatOpenAI(model="gpt-4o")
# All workers sharing this Redis instance will benefit from the same cache
print(llm.invoke("What is 2+2?").content)
```

---

## 9.3 Redis + CrewAI with TTL

Combine Redis persistence with a TTL policy for automatic expiration.

```python
from chengeta_ai import CacheManager, CacheKeyBuilder, TTLPolicy
from chengeta_ai.backends.redis_backend import RedisBackend
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

manager = CacheManager(
    backend=RedisBackend(url="redis://localhost:6379/2"),
    key_builder=CacheKeyBuilder(namespace="crew"),
    ttl_policy=TTLPolicy(default_ttl=7200),  # 2-hour cache
)

cached_crew = CrewAICacheAdapter(crew, manager)
result = cached_crew.kickoff(inputs={"topic": "AI safety"})
```
