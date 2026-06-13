---
title: "LangChain"
---

# LangChain

Integrate chengeta-ai with LangChain for automatic LLM response caching,
embedding caching, and cache invalidation.

```bash
pip install 'chengeta-ai[langchain]'
```

---

## 2.1 Drop-in global LLM cache

Register once at app startup -- every `ChatOpenAI` / `ChatAnthropic` call is
automatically cached.

```python
from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="lc"),
)
set_llm_cache(LangChainCacheAdapter(manager))

llm = ChatOpenAI(model="gpt-4o")

# First call — hits OpenAI
response1 = llm.invoke("What is the capital of France?")

# Second call — served from cache, 0 tokens used
response2 = llm.invoke("What is the capital of France?")

assert response1.content == response2.content
print("Cache working:", response1.content)
```

---

## 2.2 Per-chain cache with disk backend

Use a persistent disk backend so cached results survive server restarts.

```python
from langchain_core.globals import set_llm_cache
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

# Persistent cache — survives server restarts
manager = CacheManager(
    backend=DiskBackend(directory="/var/cache/langchain"),
    key_builder=CacheKeyBuilder(namespace="lc"),
)
set_llm_cache(LangChainCacheAdapter(manager))

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini")

result = chain.invoke({"question": "Explain RAG in one sentence."})
print(result.content)
```

---

## 2.3 Async chain with cached embeddings

Cache embedding vectors alongside LLM responses so repeated queries skip the embedding API call.

```python
import asyncio
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.globals import set_llm_cache
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, EmbeddingCache
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="lc"),
)
set_llm_cache(LangChainCacheAdapter(manager))
emb_cache = EmbeddingCache(manager)

embedder = OpenAIEmbeddings(model="text-embedding-3-small")

async def get_embedding(text: str):
    return emb_cache.get_or_compute(
        text=text,
        compute_fn=lambda t: embedder.embed_query(t),
        model_id="text-embedding-3-small",
    )

async def main():
    vec1 = await get_embedding("What is machine learning?")
    vec2 = await get_embedding("What is machine learning?")  # from cache
    assert (vec1 == vec2).all()
    print("Embedding cache hit confirmed, shape:", vec1.shape)

asyncio.run(main())
```

---

## 2.4 ResponseCache + LangChain LLMMiddleware together

Wrap a raw LLM function with `LLMMiddleware` for fine-grained caching control.

```python
from langchain_openai import ChatOpenAI
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    ResponseCache, LLMMiddleware,
)

manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder())
cache = ResponseCache(manager)
key_builder = CacheKeyBuilder(namespace="lc")

# Wrap the raw LLM function with middleware
middleware = LLMMiddleware(cache, key_builder, model_id="gpt-4o")

@middleware
def call_llm(messages: list[dict]) -> str:
    llm = ChatOpenAI(model="gpt-4o")
    return llm.invoke(messages).content

messages = [{"role": "user", "content": "Name three planets."}]
print(call_llm(messages))   # API call
print(call_llm(messages))   # Cache hit — instant
```

---

## 2.5 Cache invalidation by model

Invalidate all cached responses for a specific model -- useful when switching model versions.

```python
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    InvalidationEngine, ResponseCache,
)
from langchain_core.globals import set_llm_cache
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

tag_store = InMemoryBackend()
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="lc"),
    invalidation_engine=InvalidationEngine(tag_store),
)
set_llm_cache(LangChainCacheAdapter(manager))
rc = ResponseCache(manager)

messages = [{"role": "user", "content": "Hello"}]
rc.set(messages, "Hi there!", "gpt-4o", tags=["model:gpt-4o"])

# Invalidate everything cached for gpt-4o
count = rc.invalidate_model("gpt-4o")
print(f"Invalidated {count} cache entries for gpt-4o")
```
