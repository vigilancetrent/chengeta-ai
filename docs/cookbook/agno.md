# Agno

Cache Agno agent responses -- sync and async -- including team workflows,
tool-level caching, and multi-turn context management.

```bash
pip install 'chengeta-ai[agno]'
```

---

## 6.1 Single agent with sync caching

Wrap an Agno agent so that identical prompts return the cached response.

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="agno"),
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    description="You are a helpful assistant.",
    markdown=True,
)
cached = AgnoCacheAdapter(agent, manager)

# First call — hits the model
response1 = cached.run("Explain vector embeddings in 2 sentences.")
# Second call — instant cache hit
response2 = cached.run("Explain vector embeddings in 2 sentences.")

print(response1.content)
```

---

## 6.2 Async agent

Use the async interface for non-blocking agent calls.

```python
import asyncio
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="agno"),
)
agent = Agent(model=OpenAIChat(id="gpt-4o"), markdown=True)
cached = AgnoCacheAdapter(agent, manager)

async def main():
    r1 = await cached.arun("What year was Python created?")
    r2 = await cached.arun("What year was Python created?")  # cache hit
    print(r1.content)

asyncio.run(main())
```

---

## 6.3 Team of cached agents

Cache each agent in a team independently. Repeated runs with the same input
skip the model entirely.

```python
import asyncio
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

manager = CacheManager(
    backend=DiskBackend(directory="/var/cache/agno"),
    key_builder=CacheKeyBuilder(namespace="agno"),
)

coder   = AgnoCacheAdapter(Agent(model=OpenAIChat(id="gpt-4o"), role="Write Python code"), manager)
tester  = AgnoCacheAdapter(Agent(model=OpenAIChat(id="gpt-4o-mini"), role="Write tests"), manager)

async def main():
    code    = await coder.arun("Write a function that computes Fibonacci numbers.")
    tests   = await tester.arun(f"Write pytest tests for:\n{code.content}")
    print("Code:\n", code.content)
    print("Tests:\n", tests.content)

asyncio.run(main())
```

---

## 6.4 Agno agent with tool calls -- cache at tool level

Cache search results at the tool level so repeated queries skip the web call.

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, RetrievalCache
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder())
ret_cache = RetrievalCache(manager)

# Cache search results so repeated queries skip the web call
def cached_search(query: str) -> list[str]:
    def do_search(q: str) -> list[str]:
        return DuckDuckGoTools().search(q)

    return ret_cache.get_or_retrieve(
        query=query,
        retrieve_fn=do_search,
        retriever_id="duckduckgo",
        top_k=5,
    )

agent = Agent(model=OpenAIChat(id="gpt-4o-mini"), tools=[DuckDuckGoTools()])
cached_agent = AgnoCacheAdapter(agent, manager)

response = cached_agent.run("Latest news about AI regulation in 2025")
print(response.content)
```

---

## 6.5 Context cache for multi-turn sessions

Store and retrieve per-session conversation history, then invalidate it when done.

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    ContextCache, InvalidationEngine,
)
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

tag_store = InMemoryBackend()
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="agno"),
    invalidation_engine=InvalidationEngine(tag_store),
)
ctx_cache = ContextCache(manager)
agent = Agent(model=OpenAIChat(id="gpt-4o-mini"))
cached = AgnoCacheAdapter(agent, manager)

SESSION = "user-42"

# Store turns in context cache
ctx_cache.set(SESSION, 0, [{"role": "user", "content": "My name is Alice."}])
ctx_cache.set(SESSION, 1, [{"role": "assistant", "content": "Hello Alice!"}])

# Retrieve history
history = ctx_cache.get(SESSION, 0)
print("History:", history)

# End of session — clear context
ctx_cache.invalidate_session(SESSION)
```
