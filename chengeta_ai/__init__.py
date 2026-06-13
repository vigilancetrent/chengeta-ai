"""chengeta-ai — Unified caching layer for AI/agent frameworks.

Quick start::

    from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder

    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(),
    )
    manager.set("my_key", {"result": 42}, ttl=60)
    value = manager.get("my_key")

From settings::

    from chengeta_ai import CacheManager, ChengetaSettings

    manager = CacheManager.from_settings(ChengetaSettings(backend="disk"))

Optional backends (require extras)::

    from chengeta_ai.backends.redis_backend import RedisBackend         # [redis]
    from chengeta_ai.backends.vector_backend import FAISSBackend        # [vector-faiss]
    from chengeta_ai.backends.vector_backend import ChromaBackend       # [vector-chroma]
    from chengeta_ai.backends.vector_backend import QdrantBackend       # [vector-qdrant]
    from chengeta_ai.backends.vector_backend import WeaviateBackend     # [vector-weaviate]

Framework adapters (require framework extras)::

    from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
    from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter
    from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter
    from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter
    from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter
    from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter
    from chengeta_ai.adapters.openai_adapter import OpenAICacheAdapter
    from chengeta_ai.adapters.anthropic_adapter import AnthropicCacheAdapter
    from chengeta_ai.adapters.google_adk_adapter import GoogleADKCacheAdapter
    from chengeta_ai.adapters.openai_agents_adapter import OpenAIAgentsCacheAdapter
    from chengeta_ai.adapters.llamaindex_adapter import LlamaIndexLLMCacheAdapter
    from chengeta_ai.adapters.claude_agent_adapter import ClaudeAgentCacheAdapter
"""

from __future__ import annotations

# Config
from chengeta_ai.config.settings import ChengetaSettings

# Protocols
from chengeta_ai.backends.base import CacheBackend, VectorBackend
from chengeta_ai.backends.async_base import AsyncCacheBackend

# Core backends (no optional deps)
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.backends.disk_backend import DiskBackend
from chengeta_ai.backends.tiered_backend import TieredBackend
from chengeta_ai.backends.async_memory_backend import AsyncInMemoryBackend

# Core engine
from chengeta_ai.core.compressor import Compressor, GzipCompressor, NoopCompressor
from chengeta_ai.core.key_builder import CacheKeyBuilder
from chengeta_ai.core.metrics import CacheMetrics
from chengeta_ai.core.policies import TTLPolicy, EvictionPolicy
from chengeta_ai.core.invalidation import InvalidationEngine
from chengeta_ai.core.request_config import RequestConfig
from chengeta_ai.core.serializer import JsonSerializer, PickleSerializer, Serializer
from chengeta_ai.core.stampede import StampedeShield
from chengeta_ai.core.warmer import CacheWarmer
from chengeta_ai.core.cache_manager import CacheManager

# Cache layers
from chengeta_ai.layers.adaptive_semantic_cache import AdaptiveSemanticCache
from chengeta_ai.layers.embedding_cache import EmbeddingCache
from chengeta_ai.layers.retrieval_cache import RetrievalCache
from chengeta_ai.layers.context_cache import ContextCache
from chengeta_ai.layers.prompt_cache import PromptCacheLayer
from chengeta_ai.layers.response_cache import ResponseCache
from chengeta_ai.layers.semantic_cache import SemanticCache
from chengeta_ai.layers.streaming_cache import StreamingResponseCache

# Middleware
from chengeta_ai.middleware.llm_middleware import LLMMiddleware, AsyncLLMMiddleware
from chengeta_ai.middleware.embedding_middleware import EmbeddingMiddleware
from chengeta_ai.middleware.retriever_middleware import RetrieverMiddleware

__version__ = "0.3.0"

__all__ = [
    # Config
    "ChengetaSettings",
    # Protocols
    "CacheBackend",
    "VectorBackend",
    "AsyncCacheBackend",
    # Backends
    "InMemoryBackend",
    "DiskBackend",
    "TieredBackend",
    "AsyncInMemoryBackend",
    # Core
    "CacheKeyBuilder",
    "CacheMetrics",
    "TTLPolicy",
    "EvictionPolicy",
    "InvalidationEngine",
    "RequestConfig",
    "Compressor",
    "GzipCompressor",
    "NoopCompressor",
    "Serializer",
    "PickleSerializer",
    "JsonSerializer",
    "StampedeShield",
    "CacheWarmer",
    "CacheManager",
    # Layers
    "AdaptiveSemanticCache",
    "EmbeddingCache",
    "RetrievalCache",
    "ContextCache",
    "PromptCacheLayer",
    "ResponseCache",
    "SemanticCache",
    "StreamingResponseCache",
    # Middleware
    "LLMMiddleware",
    "AsyncLLMMiddleware",
    "EmbeddingMiddleware",
    "RetrieverMiddleware",
]
