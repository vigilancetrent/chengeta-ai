"""LangChain support assistant using local Ollama + chengeta-ai.

Run:
    uv run python -m cookbook.langchain.agent
"""

from __future__ import annotations
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.globals import set_llm_cache

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODEL = "gemma3:4b"


def build_chain() -> tuple[CacheManager, ChatPromptTemplate, ChatOllama]:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-langchain"),
    )
    set_llm_cache(LangChainCacheAdapter(manager))

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior support engineer. Provide concise, accurate customer replies "
                "based only on policy context and ticket details.",
            ),
            (
                "human",
                "Policy snippets:\n{policies}\n\n"
                "Customer ticket:\n{ticket}\n\n"
                "Return: summary, root-cause hypothesis, and clear next steps.",
            ),
        ]
    )

    llm = ChatOllama(model=MODEL, temperature=0)
    return manager, prompt, llm


def main() -> None:
    _manager, prompt, llm = build_chain()
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

    t0 = time.perf_counter()
    r1 = chain.invoke(inputs)
    t1 = time.perf_counter()
    print("=== First Run (LLM call expected) ===")
    print(r1.content)
    print(f"Time: {t1 - t0:.3f}s")

    t2 = time.perf_counter()
    r2 = chain.invoke(inputs)
    t3 = time.perf_counter()
    print("\n=== Second Run (cache hit expected) ===")
    print(r2.content)
    print(f"Time: {t3 - t2:.3f}s")
    print(f"\nSpeedup: {(t1 - t0) / (t3 - t2):.1f}x faster")


if __name__ == "__main__":
    main()
