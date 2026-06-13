from __future__ import annotations
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent

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
    t0 = time.perf_counter()
    r1 = await cached.arun(q)
    t1 = time.perf_counter()
    print("=== AutoGen First Run ===")
    print(r1)
    print(f"Time: {t1 - t0:.3f}s")

    t2 = time.perf_counter()
    r2 = await cached.arun(q)
    t3 = time.perf_counter()
    print("\n=== AutoGen Second Run (cache hit expected) ===")
    print(r2)
    print(f"Time: {t3 - t2:.3f}s  ({(t1 - t0) / (t3 - t2):.0f}x faster)")


if __name__ == "__main__":
    asyncio.run(main())
