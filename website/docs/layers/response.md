---
title: "ResponseCache"
---

# ResponseCache

Cache LLM completions so identical prompts never hit the API twice.

---

## Overview

`ResponseCache` stores the full response object returned by an LLM provider, keyed by a composite of:

- **model ID** -- distinguishes responses from different models (e.g. `gpt-4` vs `claude-3`).
- **messages hash** -- SHA-256 digest of the serialized message list.
- **params hash** -- SHA-256 digest of generation parameters (temperature, max_tokens, etc.).

The cache uses `pickle` for serialization, so any Python object that is picklable can be stored -- raw strings, Pydantic models, or full SDK response objects.

**When to use:** Any time you call an LLM with deterministic, non-personalized prompts -- classification, extraction, summarization of static content, tool-calling chains that replay the same messages.

:::warning[Non-deterministic prompts]
If your prompt includes timestamps, random IDs, or per-user data, those values become part of the key and will prevent cache hits. Strip volatile fields before caching or move them into a separate context layer.
:::


---

## Usage

### Basic get / set

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.layers.response_cache import ResponseCache

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
)
cache = ResponseCache(manager)

messages = [{"role": "user", "content": "Translate 'hello' to French."}]

# Store a response
cache.set(messages, "Bonjour", model_id="gpt-4", ttl=3600)

# Retrieve it
result = cache.get(messages, model_id="gpt-4")
print(result)  # "Bonjour"
```

### get_or_generate -- compute on miss

```python
def call_llm(msgs):
    return openai.chat.completions.create(
        model="gpt-4", messages=msgs
    )

# Returns cached value if available; otherwise calls call_llm,
# caches the result, and returns it.
response = cache.get_or_generate(
    messages=messages,
    generate_fn=call_llm,
    model_id="gpt-4",
    ttl=3600,
)
```

### Invalidate all entries for a model

```python
removed = cache.invalidate_model("gpt-4")
print(f"Removed {removed} cached responses")
```

---

## How It Works

1. **Key construction** -- `_build_key` hashes the message list and the params dict independently using SHA-256 (truncated to 16 hex chars), then delegates to `CacheKeyBuilder.build()` which produces a key like `chengeta:resp:a3f9b2c1d4e5f678`.
2. **Serialization** -- Responses are serialized with `pickle.dumps` on write and deserialized with `pickle.loads` on read.
3. **Storage** -- The pickled bytes are passed to `CacheManager.set()`, which applies the TTL policy and routes to the configured backend.
4. **Tagging** -- Each entry is tagged `model:{model_id}` by default, enabling bulk invalidation via `invalidate_model()`.

```
messages + params
       |
       v
  _build_key()
  SHA-256(messages) + SHA-256(params)
       |
       v
  CacheKeyBuilder.build("response", hash, extra={model, params_hash})
       |
       v
  "chengeta:resp:a3f9b2c1d4e5f678"
```

---

## API Reference

### Constructor

| Parameter | Type | Default | Description |
|---|---|---|---|
| `manager` | `CacheManager` | *required* | The underlying cache manager instance. |

### Methods

| Method | Parameters | Returns | Description |
|---|---|---|---|
| `get` | `messages: list`, `model_id: str = "default"`, `params: dict \| None = None` | `Any \| None` | Return the cached response, or `None` on miss. |
| `set` | `messages: list`, `response: Any`, `model_id: str = "default"`, `params: dict \| None = None`, `ttl: int \| None = None`, `tags: list[str] \| None = None` | `None` | Store a response in the cache. Tags default to `["model:{model_id}"]`. |
| `get_or_generate` | `messages: list`, `generate_fn: Callable[[list], Any]`, `model_id: str = "default"`, `params: dict \| None = None`, `ttl: int \| None = None` | `Any` | Return cached response or call `generate_fn`, cache, and return the result. |
| `invalidate_model` | `model_id: str` | `int` | Remove all cached responses tagged with the given model. Returns the number of keys removed. |

:::tip[Params affect the key]
If you call the same prompt with `temperature=0.0` and later with `temperature=0.7`, these are separate cache entries. Pass the same `params` dict to get a hit.
:::


---

## Source

 `chengeta_ai/layers/response_cache.py`
