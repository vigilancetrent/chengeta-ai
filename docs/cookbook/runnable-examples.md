# Runnable Examples

Complete, tested examples from the `cookbook/` directory — every example was verified against a local **Ollama** instance running `gemma3:4b`.

Each example runs two passes to show the **first run (LLM call)** and the **second run (cache hit)**.

---

## Prerequisites

**Ollama** running with `gemma3:4b`:

```bash
ollama serve
ollama pull gemma3:4b
```

**Install the package + extras** (from the repo root):

```bash
# Core (covers Tier 1 examples — no Ollama needed)
uv pip install -e .

# Framework adapters + Ollama integration
uv pip install "chengeta-ai[langchain,langgraph,autogen,crewai,agno]"
uv pip install langchain-ollama autogen-agentchat litellm

# Optional backends
uv pip install faiss-cpu redis
```

Or install everything at once:

```bash
uv sync --all-extras
```

---

## Test Runner

Run all examples automatically with the tiered test runner:

```bash
# Tier 1 only — no Ollama needed (core, ttl, invalidation)
uv run python cookbook/run_all.py

# Tier 1 + 2 — framework adapters (needs Ollama + gemma3:4b)
uv run python cookbook/run_all.py --full

# Everything including optional backends (redis, faiss)
uv run python cookbook/run_all.py --all
```

Expected output:

```
chengeta-ai cookbook -- running 10 examples
------------------------------------------------------------
  Core: ResponseCache + EmbeddingCache          OK    (50.2s)
  TTL: per-type retention policy                OK    (1.1s)
  Invalidation: tag-based bulk eviction         OK    (1.1s)
  LangChain: support assistant chain            OK    (21.0s)
  LangGraph: incident triage graph              OK    (70.0s)
  AutoGen: async assistant                      OK    (88.9s)
  CrewAI: release planning crew                 OK    (281.3s)
  Agno: deployment risk analyst                 OK    (72.0s)
  A2A: planner-executor-reviewer                OK    (358.8s)
  Multi-Framework: LangChain + A2A              OK    (128.5s)
------------------------------------------------------------
  passed=10  failed=0  skipped=0
```

---

## Tier 1 — Base Examples (no Ollama required)

### Core: ResponseCache + EmbeddingCache

```bash
uv run python -m cookbook.core.agent
```

```python
"""Core caching layers quick demo."""

from chengeta_ai import (
    CacheKeyBuilder, CacheManager, EmbeddingCache,
    InMemoryBackend, ResponseCache,
)
from langchain_ollama import ChatOllama, OllamaEmbeddings


def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-core"),
    )
    rcache = ResponseCache(manager)
    ecache = EmbeddingCache(manager)

    llm = ChatOllama(model="gemma3:4b", temperature=0)
    messages = [{"role": "user", "content": "Give 3 release safety checks."}]

    def call(msgs):
        return llm.invoke(msgs).content

    r1 = rcache.get_or_generate(messages, call, model_id="gemma3:4b")
    r2 = rcache.get_or_generate(messages, call, model_id="gemma3:4b")
    print("=== Response Cache ===")
    print(r1)
    print("cache_hit_same:", r1 == r2)

    print("\n=== Embedding Cache ===")
    try:
        emb = OllamaEmbeddings(model="nomic-embed-text")
        vec1 = ecache.get_or_compute(
            text="payment webhook timeout error",
            compute_fn=lambda t: emb.embed_query(t),
            model_id="nomic-embed-text",
        )
        vec2 = ecache.get_or_compute(
            text="payment webhook timeout error",
            compute_fn=lambda t: emb.embed_query(t),
            model_id="nomic-embed-text",
        )
        print("vector_length:", len(vec1))
        print("cache_hit_same:", list(vec1) == list(vec2))
    except Exception as exc:
        print("embedding_demo_skipped:", exc)


if __name__ == "__main__":
    main()
```

---

### TTL: Per-Type Retention Policy

```bash
uv run python -m cookbook.ttl.agent
```

```python
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend, TTLPolicy


def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-ttl"),
        ttl_policy=TTLPolicy(
            default_ttl=60,
            per_type={"response": 10, "embed": 3600},
        ),
    )
    manager.set("demo", "ok", cache_type="response")
    print("stored key with response ttl policy")


if __name__ == "__main__":
    main()
```

---

### Invalidation: Tag-Based Bulk Eviction

```bash
uv run python -m cookbook.invalidation.agent
```

```python
from chengeta_ai import (
    CacheKeyBuilder, CacheManager, InMemoryBackend, InvalidationEngine,
)


def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-inv"),
        invalidation_engine=InvalidationEngine(InMemoryBackend()),
    )
    manager.set("k1", "v1", tags=["model:gemma3:4b"])
    manager.set("k2", "v2", tags=["model:gemma3:4b"])
    print("invalidated:", manager.invalidate("model:gemma3:4b"))


if __name__ == "__main__":
    main()
```

---

## Tier 2 — Framework Examples (requires Ollama + `gemma3:4b`)

### LangChain: Support Assistant Chain

```bash
uv run python -m cookbook.langchain.agent
```

```python
"""LangChain support assistant using local Ollama + chengeta-ai."""

from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.globals import set_llm_cache


MODEL = "gemma3:4b"


def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-langchain"),
    )
    set_llm_cache(LangChainCacheAdapter(manager))

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a senior support engineer. Provide concise, accurate customer "
         "replies based only on policy context and ticket details."),
        ("human",
         "Policy snippets:\n{policies}\n\n"
         "Customer ticket:\n{ticket}\n\n"
         "Return: summary, root-cause hypothesis, and clear next steps."),
    ])
    llm = ChatOllama(model=MODEL, temperature=0)
    chain = prompt | llm

    inputs = {
        "policies": (
            "1) Refunds allowed within 48h if duplicate charge confirmed.\n"
            "2) Escalate payment gateway incidents when failure rate > 5%.\n"
            "3) Share ETA only after engineering confirmation."
        ),
        "ticket": (
            "Customer reports two charges for one order. One succeeded, one pending hold. "
            "Wants immediate refund and asks if account is compromised."
        ),
    }

    r1 = chain.invoke(inputs)
    print("=== First Run (LLM call expected) ===")
    print(r1.content)

    r2 = chain.invoke(inputs)
    print("\n=== Second Run (cache hit expected) ===")
    print(r2.content)


if __name__ == "__main__":
    main()
```

---

### LangGraph: Incident Triage Graph

```bash
uv run python -m cookbook.langgraph.agent
```

```python
"""LangGraph incident triage agent using local Ollama + chengeta-ai."""

from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from langgraph.graph.message import add_messages
from langgraph.graph import END, StateGraph
from langchain_ollama import ChatOllama
from langchain_core.globals import set_llm_cache
from typing import Annotated
from typing_extensions import TypedDict

MODEL = "gemma3:4b"


class IncidentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    severity: str
    action_plan: str


def build_graph(llm):
    def classify_severity(state):
        prompt = [
            ("system", "Classify incident severity as LOW, MEDIUM, HIGH, or CRITICAL. "
                       "Return only one word."),
            *state.get("messages", []),
        ]
        return {"severity": llm.invoke(prompt).content.strip().upper()}

    def generate_action_plan(state):
        plan = llm.invoke([
            ("system", "You are a senior SRE. Create a concise response plan with: "
                       "Immediate containment, diagnostics, stakeholder comms, and follow-up."),
            ("human", f"Severity: {state.get('severity')}\n"
                      f"Report: {state.get('messages', [])[-1]}"),
        ]).content
        return {"action_plan": plan, "messages": [("assistant", plan)]}

    graph = StateGraph(IncidentState)
    graph.add_node("classify_severity", classify_severity)
    graph.add_node("generate_action_plan", generate_action_plan)
    graph.set_entry_point("classify_severity")
    graph.add_edge("classify_severity", "generate_action_plan")
    graph.add_edge("generate_action_plan", END)
    return graph


def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-langgraph"),
    )
    set_llm_cache(LangChainCacheAdapter(manager))

    llm = ChatOllama(model=MODEL, temperature=0)
    app = build_graph(llm).compile(checkpointer=LangGraphCacheAdapter(manager))

    thread = {"configurable": {"thread_id": "incident-001"}}
    incident = {
        "messages": [("user",
                       "Payment API p95 latency jumped from 300ms to 8s after deployment. "
                       "5xx error rate is now 18% in ap-south region and rising.")],
        "severity": "",
        "action_plan": "",
    }

    result1 = app.invoke(incident, config=thread)
    print("=== First Run ===")
    print("Severity:", result1["severity"])
    print("Plan:\n", result1["action_plan"])

    result2 = app.invoke(incident, config=thread)
    print("\n=== Second Run (cache/checkpoint hit expected) ===")
    print("Severity:", result2["severity"])


if __name__ == "__main__":
    main()
```

---

### AutoGen: Async Assistant

```bash
uv run python -m cookbook.autogen.agent
```

```python
"""AutoGen async assistant using local Ollama + chengeta-ai."""

import asyncio
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent


async def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-autogen"),
    )
    model_client = OpenAIChatCompletionClient(
        model="gemma3:4b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        model_info={
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "structured_output": False,
            "family": "unknown",
        },
    )
    agent = AssistantAgent("assistant", model_client=model_client)
    cached = AutoGenCacheAdapter(agent, manager)

    q = "Give a 5-point migration plan for moving sync webhooks to async processing"
    r1 = await cached.arun(q)
    r2 = await cached.arun(q)
    print("=== AutoGen First Run ===")
    print(r1)
    print("\n=== AutoGen Second Run (cache hit expected) ===")
    print(r2)


if __name__ == "__main__":
    asyncio.run(main())
```

:::note
`autogen-agentchat` is a separate package from `autogen-core` and `autogen-ext`. Install it explicitly:
```bash
uv add autogen-agentchat
```
The `model_info` dict is required for non-OpenAI models in autogen-ext 0.7.x.
:::

---

### CrewAI: Release Planning Crew

```bash
uv run python -m cookbook.crewai.agent
```

```python
"""CrewAI release planning crew using local Ollama + chengeta-ai."""

from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from crewai import Agent, Crew, Process, Task


MODEL = "gemma3:4b"


def build_release_crew():
    try:
        from crewai import LLM
        llm = LLM(model=f"ollama/{MODEL}", base_url="http://localhost:11434")
    except Exception:
        llm = f"ollama/{MODEL}"

    reliability_engineer = Agent(
        role="Reliability Engineer",
        goal="Identify deployment failure modes and mitigation controls",
        backstory="Owns SLOs and incident response for mission-critical services.",
        llm=llm,
        verbose=False,
    )
    release_manager = Agent(
        role="Release Manager",
        goal="Produce a ship/no-ship recommendation and launch checklist",
        backstory="Coordinates releases across engineering, support, and operations.",
        llm=llm,
        verbose=False,
    )
    risk_task = Task(
        description=(
            "Analyze this release context and provide:\n"
            "- top risks\n- blast radius\n- pre-deploy safeguards\n"
            "Context: {release_context}"
        ),
        expected_output="Structured risk analysis with severity and mitigations.",
        agent=reliability_engineer,
    )
    plan_task = Task(
        description=(
            "Using the risk analysis, produce:\n"
            "- deployment checklist\n- rollback triggers\n"
            "- comms plan for stakeholders\n- final Go/No-Go decision"
        ),
        expected_output="Actionable release plan for engineering leadership.",
        agent=release_manager,
    )
    return Crew(
        agents=[reliability_engineer, release_manager],
        tasks=[risk_task, plan_task],
        process=Process.sequential,
        verbose=False,
    )


def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-crewai"),
    )
    cached_crew = CrewAICacheAdapter(build_release_crew(), manager)

    inputs = {
        "release_context": (
            "Service: payments-api; change: retries + webhook async pipeline; "
            "traffic: 2.1M requests/day; known issue: timeout test instability."
        )
    }

    out1 = cached_crew.kickoff(inputs=inputs)
    print("=== First Run (full crew execution expected) ===")
    print(out1)

    out2 = cached_crew.kickoff(inputs=inputs)
    print("\n=== Second Run (cache hit expected) ===")
    print(out2)


if __name__ == "__main__":
    main()
```

:::note
CrewAI requires `litellm` for Ollama model routing. Install it with `uv add litellm`.
:::

---

### Agno: Deployment Risk Analyst

```bash
uv run python -m cookbook.agno.agent
```

```python
"""Agno deployment-risk analyst using local Ollama + chengeta-ai."""

import importlib
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend


MODEL = "gemma3:4b"
OLLAMA_OPENAI_BASE_URL = "http://localhost:11434/v1"


def build_agent():
    try:
        ollama_mod = importlib.import_module("agno.models.ollama")
        model = getattr(ollama_mod, "Ollama")(id=MODEL)
    except Exception:
        openai_mod = importlib.import_module("agno.models.openai")
        model = getattr(openai_mod, "OpenAIChat")(
            id=MODEL, base_url=OLLAMA_OPENAI_BASE_URL, api_key="ollama"
        )
    agent_cls = getattr(importlib.import_module("agno.agent"), "Agent")
    return agent_cls(
        model=model,
        description=(
            "You are a release risk analyst for a SaaS platform. "
            "Output concise engineering memos with risk levels and mitigation steps."
        ),
        markdown=True,
    )


def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-agno"),
    )
    cached_agent = AgnoCacheAdapter(build_agent(), manager)

    notes = (
        "Release v2.14 deploys new payment retry logic, upgrades Redis client, "
        "and adds async webhook ingestion path. One flaky integration test remains "
        "for timeout handling on partner callbacks."
    )
    prompt = f"Analyze the release notes and produce a deployment risk memo:\n{notes}"

    memo1 = cached_agent.run(prompt).content
    print("=== First Run (LLM call expected) ===")
    print(memo1)

    memo2 = cached_agent.run(prompt).content
    print("\n=== Second Run (cache hit expected) ===")
    print(memo2)


if __name__ == "__main__":
    main()
```

---

### A2A: Planner-Executor-Reviewer Pipeline

```bash
uv run python -m cookbook.a2a.agent
```

```python
"""A2A multi-agent pipeline using local Ollama + chengeta-ai."""

import asyncio
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend, TTLPolicy
from langchain_ollama import ChatOllama


MODEL = "gemma3:4b"


def llm_call(system: str, user: str) -> str:
    return ChatOllama(model=MODEL, temperature=0).invoke(
        [("system", system), ("human", user)]
    ).content


async def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-a2a"),
        ttl_policy=TTLPolicy(default_ttl=3600),
    )

    planner = A2ACacheAdapter(manager, agent_id="planner")
    executor = A2ACacheAdapter(manager, agent_id="executor")
    reviewer = A2ACacheAdapter(manager, agent_id="reviewer")

    async def plan(payload):
        return {
            "goal": payload["goal"],
            "plan": llm_call(
                "You are a technical planner. Produce 5 implementation steps.",
                payload["goal"],
            ),
        }

    async def execute(payload):
        return {
            **payload,
            "execution": llm_call(
                "You are a senior engineer. Convert plan into actionable execution checklist.",
                payload["plan"],
            ),
        }

    async def review(payload):
        return {
            **payload,
            "review": llm_call(
                "You are an engineering manager. Review for risk, missing safeguards, and rollout gates.",
                payload["execution"],
            ),
        }

    async def pipeline(goal: str) -> dict:
        p = await planner.aprocess(plan, {"goal": goal})
        e = await executor.aprocess(execute, p)
        return await reviewer.aprocess(review, e)

    goal = "Design a safe rollout plan for migrating payment webhooks to async ingestion"

    out1 = await pipeline(goal)
    print("=== First Run (three LLM stages expected) ===")
    print(out1["review"])

    out2 = await pipeline(goal)
    print("\n=== Second Run (A2A cache hits expected) ===")
    print(out2["review"])


if __name__ == "__main__":
    asyncio.run(main())
```

---

### Multi-Framework: Shared CacheManager (LangChain + A2A)

```bash
uv run python -m cookbook.multi_framework.agent
```

```python
"""Shared CacheManager across LangChain and A2A agents."""

import asyncio
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.globals import set_llm_cache


async def main() -> None:
    # Single CacheManager shared across both frameworks
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-multi"),
    )

    set_llm_cache(LangChainCacheAdapter(manager))
    llm = ChatOllama(model="gemma3:4b", temperature=0)

    planner_chain = ChatPromptTemplate.from_messages([
        ("system", "Create a concise release outline."),
        ("human", "{topic}"),
    ]) | llm

    reviewer = A2ACacheAdapter(manager, agent_id="reviewer")

    async def review_fn(payload):
        text = llm.invoke([
            ("system", "Review this outline and add two risk controls."),
            ("human", payload["outline"]),
        ]).content
        return {"reviewed": text}

    topic = "Reducing checkout latency using caching and async webhook processing"
    outline = planner_chain.invoke({"topic": topic}).content
    reviewed1 = await reviewer.aprocess(review_fn, {"outline": outline})
    reviewed2 = await reviewer.aprocess(review_fn, {"outline": outline})

    print("=== Multi-Framework First Run ===")
    print(reviewed1["reviewed"])
    print("\n=== Multi-Framework Second Run (cache hit expected) ===")
    print(reviewed2["reviewed"])


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Tier 3 — Optional Backends

### Semantic Cache: FAISS + Deterministic Embedding

```bash
uv run python -m cookbook.semantic_cache.agent
```

```python
"""Semantic cache with FAISS vector similarity — no external embedding model needed.

Uses a deterministic hash-based embedding for demonstration.
For production, swap mock_embed for a real embedding model:
    from langchain_ollama import OllamaEmbeddings
    emb = OllamaEmbeddings(model="nomic-embed-text")
    embed_fn = lambda t: np.array(emb.embed_query(t), dtype=np.float32)
"""

import hashlib
import numpy as np
from chengeta_ai.backends.vector_backend import FAISSBackend
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai import SemanticCache

DIM = 1536


def mock_embed(text: str) -> np.ndarray:
    """Deterministic unit-vector embedding based on text hash."""
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(DIM).astype(np.float32)
    return v / np.linalg.norm(v)


def main() -> None:
    cache = SemanticCache(
        exact_backend=InMemoryBackend(),
        vector_backend=FAISSBackend(dim=DIM),
        embed_fn=mock_embed,
        threshold=1.0,  # exact match only with deterministic embedding
    )

    q1 = "How to reduce p95 latency?"
    answer = "Profile hot path, add caching, optimize DB queries."

    cache.set(q1, answer)
    print("=== Exact hit (same text) ===")
    print(cache.get(q1))

    print("\n=== Miss (different text, different hash) ===")
    print(cache.get("How can I lower p95 response latency?"))  # None

    print("\n=== Direct exact cache hit ===")
    cache.set("What is p95 latency optimization?", "Measure, profile, then cache hot paths.")
    print(cache.get("What is p95 latency optimization?"))


if __name__ == "__main__":
    main()
```

:::note
For real semantic similarity (not just exact match), replace `mock_embed` with a proper embedding model and lower the threshold to ~0.85–0.95.
:::

---

### Redis: Shared Backend

```bash
uv run python -m cookbook.redis.agent
```

Requires a Redis server on `localhost:6379`.

```python
from chengeta_ai.backends.redis_backend import RedisBackend
from chengeta_ai import CacheKeyBuilder, CacheManager


def main() -> None:
    manager = CacheManager(
        backend=RedisBackend(url="redis://localhost:6379/0", key_prefix="cookbook:"),
        key_builder=CacheKeyBuilder(namespace="cookbook-redis"),
    )
    manager.set("redis_demo", {"status": "ok"}, ttl=120)
    print("redis value:", manager.get("redis_demo"))


if __name__ == "__main__":
    main()
```

---

## Example Index

| Example | Tier | Cache Feature | Deps |
|---|---|---|---|
| `core` | base | ResponseCache, EmbeddingCache | none |
| `ttl` | base | TTLPolicy per_type | none |
| `invalidation` | base | InvalidationEngine, tag eviction | none |
| `langchain` | framework | LangChainCacheAdapter, set_llm_cache | langchain-ollama |
| `langgraph` | framework | LangGraphCacheAdapter, checkpointer | langgraph, langchain-ollama |
| `autogen` | framework | AutoGenCacheAdapter | autogen-agentchat, autogen-ext |
| `crewai` | framework | CrewAICacheAdapter, kickoff cache | crewai, litellm |
| `agno` | framework | AgnoCacheAdapter | agno |
| `a2a` | framework | A2ACacheAdapter, aprocess | langchain-ollama |
| `multi_framework` | framework | Shared CacheManager across frameworks | langchain-ollama |
| `semantic_cache` | optional | SemanticCache, FAISSBackend | faiss-cpu |
| `redis` | optional | RedisBackend | redis |
