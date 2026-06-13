---
title: "AutoGen"
---

# AutoGen

Cache agent responses for both the new `autogen-agentchat` (0.4+) and legacy
`pyautogen` (0.2.x) APIs.

```bash
# New API (0.4+)
pip install 'autogen-agentchat>=0.4'

# Legacy API (0.2.x)
pip install 'chengeta-ai[autogen]'
```

---

## 4.1 autogen-agentchat 0.4+ -- AssistantAgent with async caching

Wrap an `AssistantAgent` so that repeated queries return instantly from cache.

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="ag"),
)

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
agent = AssistantAgent("assistant", model_client=model_client)
cached = AutoGenCacheAdapter(agent, manager)

async def main():
    # First call — hits the model
    result1 = await cached.arun("What is the speed of light?")
    # Second call — instant cache hit
    result2 = await cached.arun("What is the speed of light?")
    print("Same result:", result1 == result2)

asyncio.run(main())
```

---

## 4.2 autogen-agentchat 0.4+ -- RoundRobinGroupChat with cached agents

Wrap each agent independently and pass the inner agents to the team.

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=DiskBackend(directory="/var/cache/autogen"),
    key_builder=CacheKeyBuilder(namespace="ag"),
)
client = OpenAIChatCompletionClient(model="gpt-4o-mini")

# Wrap each agent independently
researcher = AutoGenCacheAdapter(
    AssistantAgent("researcher", model_client=client,
                   system_message="Research and provide facts."),
    manager,
)
summarizer = AutoGenCacheAdapter(
    AssistantAgent("summarizer", model_client=client,
                   system_message="Summarize concisely."),
    manager,
)

async def main():
    team = RoundRobinGroupChat(
        [researcher._agent, summarizer._agent],  # pass inner agents to team
        termination_condition=MaxMessageTermination(4),
    )
    result = await team.run(task="Explain transformer attention in 3 sentences.")
    print(result.messages[-1].content)

asyncio.run(main())
```

---

## 4.3 pyautogen 0.2.x -- ConversableAgent (legacy)

The adapter also works with the legacy `pyautogen` `ConversableAgent` API.

```python
from autogen import ConversableAgent, UserProxyAgent
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="ag-legacy"),
)

assistant = ConversableAgent(
    name="assistant",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "..."}]},
    system_message="You are a helpful assistant.",
)
cached_assistant = AutoGenCacheAdapter(assistant, manager)

messages = [{"role": "user", "content": "What is 10 * 10?"}]

reply1 = cached_assistant.generate_reply(messages)  # API call
reply2 = cached_assistant.generate_reply(messages)  # Cache hit

assert reply1 == reply2
print(reply1)
```

---

## 4.4 AutoGen + LangChain embeddings cached together

Share a single `CacheManager` for both agent response caching and embedding caching.

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_openai import OpenAIEmbeddings
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    EmbeddingCache, TTLPolicy,
)
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="combo"),
    ttl_policy=TTLPolicy(default_ttl=3600, per_type={"embed": 86400}),
)
emb_cache  = EmbeddingCache(manager)
embedder   = OpenAIEmbeddings(model="text-embedding-3-small")
agent      = AssistantAgent("assistant", model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"))
cached_agent = AutoGenCacheAdapter(agent, manager)

async def main():
    # Cache embeddings for retrieval context
    vec = emb_cache.get_or_compute(
        "transformer attention mechanism",
        lambda t: embedder.embed_query(t),
        model_id="text-embedding-3-small",
    )
    print("Embedding shape:", vec.shape)

    # Cache agent replies
    reply = await cached_agent.arun("What is the transformer attention mechanism?")
    print("Agent:", reply)

asyncio.run(main())
```
