# Cookbook

Practical, copy-paste-ready recipes for every supported AI framework and feature.

Each recipe is self-contained. Pick the ones relevant to your stack.

!!! tip "Want runnable code?"
    See [Runnable Examples](runnable-examples.md) — all 12 complete, tested examples verified against a local Ollama `gemma3:4b` instance with a pass/fail test runner.

---

## Framework Compatibility

| Framework | Package | Tested Versions |
|---|---|---|
| LangChain | `langchain-core` | >= 0.2, 1.x |
| LangGraph | `langgraph` | >= 0.1, 1.x |
| AutoGen (new) | `autogen-agentchat` | >= 0.4, 0.7.x |
| AutoGen (legacy) | `pyautogen` | 0.2.x |
| CrewAI | `crewai` | >= 0.28, 1.x |
| Agno | `agno` | >= 0.1, 2.x |
| A2A | `a2a-sdk` | >= 0.2, 0.3.x |

---

## Recipes by Topic

### Setup and Configuration

- [Core Recipes](core.md) — In-memory, disk, env vars, TTL policies, invalidation setup

### Framework Integration

- [LangChain](langchain.md) — Global cache, disk backend, async embeddings, middleware
- [LangGraph](langgraph.md) — State graph checkpointing, history, multi-agent
- [AutoGen](autogen.md) — 0.4+ async, group chat, 0.2.x legacy, combined embeddings
- [CrewAI](crewai.md) — Crew kickoff, async, invalidation, retrieval in tools
- [Agno](agno.md) — Sync/async agent, team pipelines, tool caching, context sessions
- [A2A](a2a.md) — Process, wrap decorator, async, multi-agent pipeline

### Advanced Features

- [Semantic Cache](semantic-cache.md) — Standalone, inside LangChain, ChromaDB backend
- [Redis Backend](redis.md) — Basic, Redis+LangChain, Redis+CrewAI+TTL
- [Tag Invalidation](invalidation.md) — By model, by session, custom deploy tags
- [TTL Policies](ttl.md) — Global, per-layer, from env, no TTL

### End-to-End

- [Multi-Framework Pipeline](multi-framework.md) — LangChain + LangGraph + Agno + A2A in one pipeline
