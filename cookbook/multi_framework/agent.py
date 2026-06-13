from __future__ import annotations
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.globals import set_llm_cache

import asyncio
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


async def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-multi"),
    )

    set_llm_cache(LangChainCacheAdapter(manager))
    llm = ChatOllama(model="gemma3:4b", temperature=0)

    planner_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Create a concise release outline."),
            ("human", "{topic}"),
        ]
    )
    planner_chain = planner_prompt | llm

    reviewer = A2ACacheAdapter(manager, agent_id="reviewer")

    async def review_fn(payload: dict) -> dict:
        text = llm.invoke(
            [
                ("system", "Review this outline and add two risk controls."),
                ("human", payload["outline"]),
            ]
        ).content
        return {"reviewed": text}

    topic = "Reducing checkout latency using caching and async webhook processing"

    t0 = time.perf_counter()
    outline = planner_chain.invoke({"topic": topic}).content
    reviewed1 = await reviewer.aprocess(review_fn, {"outline": outline})
    t1 = time.perf_counter()
    print("=== Multi-Framework First Run ===")
    print(reviewed1["reviewed"])
    print(f"Time: {t1 - t0:.3f}s")

    t2 = time.perf_counter()
    outline2 = planner_chain.invoke({"topic": topic}).content
    reviewed2 = await reviewer.aprocess(review_fn, {"outline": outline2})
    t3 = time.perf_counter()
    print("\n=== Multi-Framework Second Run (cache hit expected) ===")
    print(reviewed2["reviewed"])
    print(f"Time: {t3 - t2:.3f}s  ({(t1 - t0) / (t3 - t2):.0f}x faster)")


if __name__ == "__main__":
    asyncio.run(main())
