---
title: "ContextCache"
---

# ContextCache

Cache conversation message history so agent state survives across restarts, workers, and sessions.

---

## Overview

`ContextCache` stores lists of conversation messages keyed by:

- **session ID** -- a unique identifier for the conversation (user ID, thread ID, etc.).
- **turn index** (optional) -- a specific turn number within the conversation. When omitted, the entire conversation history for the session is stored as a single entry.

The cache uses `pickle` for serialization, so message lists can contain dicts, Pydantic models, or framework-specific message objects.

**When to use:** Multi-turn chatbots, agentic workflows that span multiple process invocations, distributed workers that need shared conversation state, or any scenario where reconstructing context from scratch is expensive.

:::tip[Turn-level vs session-level]
Store the full history without a turn index for simple chatbots. Use turn-indexed entries when you need to roll back to a specific point in the conversation or implement branching dialogue.
:::


---

## Usage

### Store and retrieve a full session

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.layers.context_cache import ContextCache

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
)
cache = ContextCache(manager)

session_id = "user-abc-thread-1"
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there! How can I help?"},
    {"role": "user", "content": "What is the weather today?"},
]

# Store the full conversation
cache.set(session_id, messages, ttl=3600)

# Retrieve it
history = cache.get(session_id)
print(len(history))  # 3
```

### Store individual turns

```python
# Store turn 0
cache.set(session_id, [{"role": "user", "content": "Hello!"}], turn_index=0)

# Store turn 1
cache.set(
    session_id,
    [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi!"},
    ],
    turn_index=1,
)

# Retrieve a specific turn
turn_1 = cache.get(session_id, turn_index=1)
print(len(turn_1))  # 2
```

### Invalidate an entire session

```python
removed = cache.invalidate_session(session_id)
print(f"Removed {removed} cached entries for session {session_id}")
```

---

## How It Works

1. **Key construction** -- `CacheKeyBuilder.build("context", session_id, extra={"turn": turn_index})` produces a key like `chengeta:ctx:e5f6a7b8c9d01234`. When `turn_index` is `None`, the `extra` dict is omitted entirely, producing a different (session-level) key.
2. **Serialization** -- Message lists are serialized with `pickle.dumps` on write and deserialized with `pickle.loads` on read.
3. **Storage** -- Pickled bytes are passed to `CacheManager.set()` with `cache_type="context"`.
4. **Tagging** -- Each entry is tagged `session:{session_id}` by default, enabling bulk invalidation via `invalidate_session()`.

```
session_id="user-abc"  +  turn_index=3
       |
       v
  CacheKeyBuilder.build("context", "user-abc", extra={"turn": 3})
       |
       v
  "chengeta:ctx:e5f6a7b8c9d01234"
       |
       v
  Backend stores: key -> pickle.dumps(messages)
```

:::note[Session invalidation uses tags]
`invalidate_session()` calls `CacheManager.invalidate("session:{session_id}")`, which removes all keys tagged with that session -- both session-level and turn-level entries. This requires that an `InvalidationEngine` is configured on the manager.
:::


---

## API Reference

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `manager` | `CacheManager` | *required* | The underlying cache manager instance. |

### Methods

| Method | Parameters | Returns | Description |
|---|---|---|---|
| `get` | `session_id: str`, `turn_index: int \| None = None` | `list \| None` | Retrieve cached message history, or `None` on miss. |
| `set` | `session_id: str`, `messages: list`, `turn_index: int \| None = None`, `ttl: int \| None = None`, `tags: list[str] \| None = None` | `None` | Store message history. Tags default to `["session:{session_id}"]`. |
| `invalidate_session` | `session_id: str` | `int` | Remove all cached context for the given session. Returns the number of keys removed. |

:::warning[No `get_or_compute` method]
Unlike other layers, `ContextCache` does not provide a `get_or_compute` convenience method. Conversation history is accumulated incrementally and cannot be generated from a single function call.
:::


---

## Source

 `chengeta_ai/layers/context_cache.py`
