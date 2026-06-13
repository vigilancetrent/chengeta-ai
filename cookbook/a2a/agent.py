"""A2A multi-agent pipeline using local Ollama + chengeta-ai.

Run:
    uv run python -m cookbook.a2a.agent
"""

from __future__ import annotations
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend, TTLPolicy
from langchain_ollama import ChatOllama

import asyncio
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODEL = "gemma3:4b"


def llm_call(system: str, user: str) -> str:
    llm = ChatOllama(model=MODEL, temperature=0)
    return llm.invoke([("system", system), ("human", user)]).content


async def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-a2a"),
        ttl_policy=TTLPolicy(default_ttl=3600),
    )

    planner = A2ACacheAdapter(manager, agent_id="planner")
    executor = A2ACacheAdapter(manager, agent_id="executor")
    reviewer = A2ACacheAdapter(manager, agent_id="reviewer")

    async def plan(payload: dict) -> dict:
        text = llm_call(
            "You are a technical planner. Produce 5 implementation steps.",
            payload["goal"],
        )
        return {"goal": payload["goal"], "plan": text}

    async def execute(payload: dict) -> dict:
        text = llm_call(
            "You are a senior engineer. Convert plan into actionable execution checklist.",
            payload["plan"],
        )
        return {"goal": payload["goal"], "plan": payload["plan"], "execution": text}

    async def review(payload: dict) -> dict:
        text = llm_call(
            "You are an engineering manager. Review for risk, missing safeguards, and rollout gates.",
            payload["execution"],
        )
        return {
            "goal": payload["goal"],
            "execution": payload["execution"],
            "review": text,
        }

    async def pipeline(goal: str) -> dict:
        p = await planner.aprocess(plan, {"goal": goal})
        e = await executor.aprocess(execute, p)
        r = await reviewer.aprocess(review, e)
        return r

    goal = "Design a safe rollout plan for migrating payment webhooks to async ingestion"

    t0 = time.perf_counter()
    out1 = await pipeline(goal)
    t1 = time.perf_counter()
    print("=== First Run (three LLM stages expected) ===")
    print(out1["review"])
    print(f"Time: {t1 - t0:.3f}s")

    t2 = time.perf_counter()
    out2 = await pipeline(goal)
    t3 = time.perf_counter()
    print("\n=== Second Run (A2A cache hits expected) ===")
    print(out2["review"])
    print(f"Time: {t3 - t2:.3f}s  ({(t1 - t0) / (t3 - t2):.0f}x faster)")


if __name__ == "__main__":
    asyncio.run(main())
