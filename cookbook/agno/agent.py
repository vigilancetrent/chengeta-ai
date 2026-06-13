"""Agno deployment-risk analyst using local Ollama + chengeta-ai.

Run:
    python cookbook/agno/agent.py
"""

from __future__ import annotations
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend

import importlib
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODEL = "gemma3:4b"
OLLAMA_OPENAI_BASE_URL = "http://localhost:11434/v1"


def _build_ollama_model() -> Any:
    """Try native Ollama model first, then OpenAI-compatible Ollama endpoint."""
    try:
        ollama_mod = importlib.import_module("agno.models.ollama")
        ollama_cls = getattr(ollama_mod, "Ollama")
        return ollama_cls(id=MODEL)
    except Exception:
        openai_mod = importlib.import_module("agno.models.openai")
        openai_cls = getattr(openai_mod, "OpenAIChat")
        return openai_cls(
            id=MODEL,
            base_url=OLLAMA_OPENAI_BASE_URL,
            api_key="ollama",
        )


def build_agent() -> Any:
    agent_mod = importlib.import_module("agno.agent")
    agent_cls = getattr(agent_mod, "Agent")
    model = _build_ollama_model()
    return agent_cls(
        model=model,
        description=(
            "You are a release risk analyst for a SaaS platform. "
            "Output concise engineering memos with risk levels and mitigation steps."
        ),
        markdown=True,
    )


def generate_memo(cached_agent: AgnoCacheAdapter, release_notes: str) -> str:
    prompt = f"""
Analyze the release notes and produce a deployment risk memo.

Include:
1) Risk level (LOW/MEDIUM/HIGH/CRITICAL)
2) Top 3 risks
3) Monitoring/alert checks to enable
4) Rollback criteria
5) Go/No-Go recommendation

Release notes:
{release_notes}
""".strip()
    return cached_agent.run(prompt).content


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

    t0 = time.perf_counter()
    memo_1 = generate_memo(cached_agent, notes)
    t1 = time.perf_counter()
    print("=== First Run (LLM call expected) ===")
    print(memo_1)
    print(f"Time: {t1 - t0:.3f}s")

    t2 = time.perf_counter()
    memo_2 = generate_memo(cached_agent, notes)
    t3 = time.perf_counter()
    print("\n=== Second Run (cache hit expected) ===")
    print(memo_2)
    print(f"Time: {t3 - t2:.3f}s  ({(t1 - t0) / (t3 - t2):.0f}x faster)")


if __name__ == "__main__":
    main()
