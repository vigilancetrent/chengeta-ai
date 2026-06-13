# chengeta-ai Cookbook

Real-world, runnable agent examples for every major framework — all backed by
`chengeta-ai` and a local **Ollama** model (`gemma3:4b`).

---

## Structure

```
cookbook/
├── run_all.py            ← test runner (see below)
│
├── core/                 ← ResponseCache + EmbeddingCache baseline
├── ttl/                  ← per-type TTL retention policy
├── invalidation/         ← tag-based bulk cache eviction
│
├── langchain/            ← LangChain support assistant + global cache
├── langgraph/            ← LangGraph incident triage with checkpointing
├── autogen/              ← AutoGen async assistant
├── crewai/               ← CrewAI multi-role release planning crew
├── agno/                 ← Agno deployment risk analyst
├── a2a/                  ← A2A planner-executor-reviewer pipeline
├── multi_framework/      ← shared CacheManager across LangChain + A2A
│
├── semantic_cache/       ← FAISS vector similarity + Ollama embeddings
└── redis/                ← RedisBackend shared-cache demo
```

Each sub-folder contains:
- `agent.py` — runnable example
- `README.md` — what it does, how to run it, integration notes

---

## Prerequisites

**1. Ollama** running with `gemma3:4b`:

```bash
ollama serve          # if not already running
ollama pull gemma3:4b
```

**2. Install the package + framework extras** (from the repo root):

```bash
# Core package (covers core/, ttl/, invalidation/ examples)
uv pip install -e .

# Framework adapters
uv pip install "chengeta-ai[langchain,langgraph,autogen,crewai,agno]"
uv pip install langchain-ollama litellm

# Optional backends
uv pip install faiss-cpu redis
```

Or use uv sync (installs everything in pyproject.toml dev extras):

```bash
uv sync --all-extras
```

---

## Running examples

**Run a single example:**

```bash
uv run python -m cookbook.core.agent
uv run python -m cookbook.langchain.agent
uv run python -m cookbook.langgraph.agent
uv run python -m cookbook.autogen.agent
uv run python -m cookbook.crewai.agent
uv run python -m cookbook.agno.agent
uv run python -m cookbook.a2a.agent
uv run python -m cookbook.multi_framework.agent
uv run python -m cookbook.semantic_cache.agent
uv run python -m cookbook.redis.agent
uv run python -m cookbook.invalidation.agent
uv run python -m cookbook.ttl.agent
```

**Run the test runner:**

```bash
# Tier 1 only — no Ollama needed (core, ttl, invalidation)
uv run python cookbook/run_all.py

# Tier 1 + 2 — framework adapters (needs Ollama + gemma3:4b)
uv run python cookbook/run_all.py --full

# Everything including optional backends (redis, faiss)
uv run python cookbook/run_all.py --all
```

---

## Example index

| Example | Cache feature | Framework deps |
|---|---|---|
| `core` | ResponseCache, EmbeddingCache | none |
| `ttl` | TTLPolicy per_type | none |
| `invalidation` | InvalidationEngine, tag eviction | none |
| `langchain` | LangChainCacheAdapter, set_llm_cache | langchain-core, langchain-ollama |
| `langgraph` | LangGraphCacheAdapter, checkpointer | langgraph, langchain-ollama |
| `autogen` | AutoGenCacheAdapter | pyautogen, autogen-ext[openai] |
| `crewai` | CrewAICacheAdapter, kickoff cache | crewai, litellm |
| `agno` | AgnoCacheAdapter | agno |
| `a2a` | A2ACacheAdapter, aprocess | langchain-ollama |
| `multi_framework` | shared CacheManager across frameworks | langchain-ollama |
| `semantic_cache` | SemanticCache, FAISSBackend | faiss-cpu, langchain-ollama |
| `redis` | RedisBackend | redis |

---

## Notes

- All framework examples produce two runs: **first run** calls the LLM, **second run** is a cache hit.
- `redis` requires a Redis server on `localhost:6379`.
- `semantic_cache` uses `gemma3:4b` for embeddings via Ollama (3072-dim).
- `crewai` requires `litellm` for Ollama model routing (`uv add litellm`).
