---
title: "Quick Start"
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Quick Start

Get caching working in 30 seconds.

---

## Step 1: Create a CacheManager

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)
```

The `CacheManager` is the central hub. It wires together a **backend** (where data is stored), a **key builder** (how keys are generated), and optional policies.

---

## Step 2: Cache a Value

```python
# Store with 60-second TTL
manager.set("my_key", b"hello world", ttl=60)

# Retrieve
value = manager.get("my_key")
print(value)  # b"hello world"

# Check existence
print(manager.exists("my_key"))  # True

# Delete
manager.delete("my_key")
```

---

## Step 3: Use a Cache Layer

Cache layers provide typed, domain-specific caching. Here's `ResponseCache` for LLM outputs:

```python
from chengeta_ai.layers.response_cache import ResponseCache

rc = ResponseCache(manager)

messages = [{"role": "user", "content": "What is 2+2?"}]

# Cache miss — returns None
print(rc.get(messages, "gpt-4"))  # None

# Store a response
rc.set(messages, "4", "gpt-4")

# Cache hit — returns "4" instantly
print(rc.get(messages, "gpt-4"))  # "4"
```

---

## Step 4: Use the Middleware Decorator

Wrap any LLM function to cache automatically:

```python
from chengeta_ai.middleware.llm_middleware import LLMMiddleware

middleware = LLMMiddleware(
    response_cache=rc,
    key_builder=CacheKeyBuilder(),
    model_id="gpt-4"
)

@middleware
def call_llm(messages):
    # This is your real LLM call
    return openai_client.chat.completions.create(
        model="gpt-4", messages=messages
    )

# First call → hits the API
result = call_llm([{"role": "user", "content": "Hello"}])

# Second call → served from cache instantly
result = call_llm([{"role": "user", "content": "Hello"}])
```

---

## Step 5: Use a Framework Adapter

<Tabs>
<TabItem value="langchain" label="LangChain">

```python
from langchain_core.globals import set_llm_cache
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

set_llm_cache(LangChainCacheAdapter(manager))
# Every LLM call is now cached automatically
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="langgraph" label="LangGraph">

```python
from langgraph.graph import StateGraph
from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter

saver = LangGraphCacheAdapter(manager)
graph = StateGraph(...).compile(checkpointer=saver)
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="crewai" label="CrewAI">

```python
from crewai import Crew
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

crew = Crew(agents=[...], tasks=[...])
cached_crew = CrewAICacheAdapter(crew, manager)
result = cached_crew.kickoff(inputs={"topic": "AI"})
```

</TabItem>

</Tabs>


---

## From Settings (Environment Variables)

For production, configure via environment variables:

```bash
export CHENGETA_BACKEND=disk
export CHENGETA_DISK_PATH=/data/cache
export CHENGETA_DEFAULT_TTL=3600
```

```python
from chengeta_ai import CacheManager, ChengetaSettings

manager = CacheManager.from_settings(ChengetaSettings.from_env())
```

---

## Next Steps

- [Configuration](configuration.md) — All settings and environment variables
- [Cache Layers](../layers/index.md) — Deep dive into each cache layer
- [Cookbook](../cookbook/index.md) — 40+ ready-to-run recipes
