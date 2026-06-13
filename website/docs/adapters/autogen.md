---
title: "AutoGenCacheAdapter"
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# AutoGenCacheAdapter

Cached agent replies for AutoGen. `AutoGenCacheAdapter` wraps any AutoGen agent with response caching, supporting both the legacy `pyautogen` 0.2.x API (`ConversableAgent.generate_reply`) and the new `autogen-agentchat` 0.4+ API (`AssistantAgent.run` / `arun`).

## Overview

AutoGen agents generate replies by calling LLMs, which incurs API costs and latency on every invocation. `AutoGenCacheAdapter` wraps an agent instance and intercepts reply generation to check the cache first. If an identical request has been seen before, the cached reply is returned instantly.

The adapter auto-detects which API generation the wrapped agent uses and exposes the appropriate cached methods. All non-overridden attributes are proxied through to the original agent via `__getattr__`, so the adapter is a transparent drop-in replacement.

**When to use:**

- You are using AutoGen agents and want to avoid redundant LLM calls for repeated inputs.
- You are running agent conversations in a loop or testing pipeline and want deterministic, fast responses for known inputs.
- You want a unified caching solution that works across AutoGen versions.

---

## Installation

<Tabs>
<TabItem value="pyautogen-0-2-x-legacy-" label="pyautogen 0.2.x (legacy)">

```bash
pip install 'chengeta-ai[autogen]'
```

This installs `pyautogen >= 0.2`.

</TabItem>

</Tabs>


<Tabs>
<TabItem value="autogen-agentchat-0-4-new-api-" label="autogen-agentchat 0.4+ (new API)">

```bash
pip install chengeta-ai 'autogen-agentchat>=0.4'
```

The `autogen-agentchat` package is not yet included in the `[autogen]` extra; install it directly.

</TabItem>

</Tabs>


---

## Usage

<Tabs>
<TabItem value="pyautogen-0-2-x" label="pyautogen 0.2.x">

```python
from autogen import ConversableAgent
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)

# Create a standard AutoGen agent
agent = ConversableAgent(
    name="assistant",
    llm_config={"model": "gpt-4o", "api_key": "..."},
)

# Wrap it with caching
cached_agent = AutoGenCacheAdapter(agent, manager)

# generate_reply is cached
messages = [{"role": "user", "content": "What is 2+2?"}]
reply = cached_agent.generate_reply(messages=messages)

# Second call returns from cache (no LLM API call)
reply = cached_agent.generate_reply(messages=messages)
```

</TabItem>

</Tabs>


<Tabs>
<TabItem value="autogen-agentchat-0-4-" label="autogen-agentchat 0.4+">

```python
from autogen_agentchat.agents import AssistantAgent
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)

agent = AssistantAgent("assistant", model_client=model_client)
cached_agent = AutoGenCacheAdapter(agent, manager)

# Async cached run
result = await cached_agent.arun("What is machine learning?")

# Second call returns from cache
result = await cached_agent.arun("What is machine learning?")
```

</TabItem>

</Tabs>


### Sync Run (0.4+ Agents)

For 0.4+ agents that support sync execution:

```python
result = cached_agent.run("Explain caching strategies")
```

:::note
The `run()` method falls back to `generate_reply()` for 0.2.x agents that do not have a `run()` method.
:::


### Transparent Proxy

The adapter forwards any attribute not explicitly overridden to the wrapped agent:

```python
cached_agent = AutoGenCacheAdapter(agent, manager)

# These all proxy through to the original agent
print(cached_agent.name)           # "assistant"
print(cached_agent.llm_config)     # {"model": "gpt-4o", ...}
```

### Multi-Agent Conversations

Wrap each agent individually to cache their replies independently:

```python
assistant = ConversableAgent(name="assistant", llm_config={...})
reviewer = ConversableAgent(name="reviewer", llm_config={...})

cached_assistant = AutoGenCacheAdapter(assistant, manager)
cached_reviewer = AutoGenCacheAdapter(reviewer, manager)
```

### With Redis Backend

```python
from chengeta_ai.backends.redis_backend import RedisBackend

manager = CacheManager(
    backend=RedisBackend(url="redis://localhost:6379/0"),
    key_builder=CacheKeyBuilder(namespace="autogen"),
)
cached_agent = AutoGenCacheAdapter(agent, manager)
```

---

## API Reference

### AutoGenCacheAdapter

**Constructor:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `agent` | `Any` | *(required)* | The AutoGen agent instance to wrap (`ConversableAgent`, `AssistantAgent`, or `UserProxyAgent`) |
| `cache_manager` | `CacheManager` | *(required)* | The Chengeta AI cache manager instance |

**Methods:**

| Method | Signature | Description |
|---|---|---|
| `generate_reply` | `(messages=None, sender=None, **kwargs) -> Any` | Cached `generate_reply` for pyautogen 0.2.x agents. Checks cache by message content before calling `agent.generate_reply()`. |
| `run` | `(message: str, **kwargs) -> Any` | Sync cached run. For 0.4+ agents, delegates to `agent.run(task=message)`. For 0.2.x agents, falls back to `generate_reply`. |
| `arun` | `(message: str, **kwargs) -> Any` | Async cached run. For 0.4+ agents, delegates to `await agent.run(task=message)`. For 0.2.x agents, falls back to `generate_reply`. |
| `__getattr__` | `(name: str) -> Any` | Transparent proxy -- forwards all non-overridden attribute accesses to the wrapped agent. |

**Cache Key Generation:**

- `generate_reply`: The cache key is built from the JSON-serialized messages list and the agent's `name` attribute.
- `run` / `arun`: The cache key is built from the message string, the agent's `name`, and any additional keyword arguments.

:::tip
The adapter uses the agent's `name` attribute as part of the cache key. Make sure each agent has a unique name if you want independent cache entries per agent.
:::


:::warning
The `arun()` method delegates cache reads and writes to synchronous `CacheManager.get()` and `CacheManager.set()` methods. Only the actual agent call (`await agent.run(...)`) is awaited. If your backend requires true async I/O, consider implementing an async cache manager.
:::


---

## Version Detection

The adapter uses the following logic to detect the AutoGen version:

1. Attempts to import `autogen_agentchat.agents.AssistantAgent` -- if successful, marks `_AUTOGEN_V2 = True`.
2. Attempts to import `autogen.ConversableAgent` -- if successful, marks `_AUTOGEN_V1 = True`.
3. At runtime, checks `isinstance(agent, AssistantAgent)` or `isinstance(agent, UserProxyAgent)` to determine which API to use.
4. If the agent has a `run()` method, `arun()` uses it; otherwise, falls back to `generate_reply()`.

This allows a single adapter class to handle both API generations transparently.
