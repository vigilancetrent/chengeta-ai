"""CrewAI release planning crew using local Ollama + chengeta-ai.

Run:
    python cookbook/crewai/agent.py
"""

from __future__ import annotations
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend
from crewai import Agent, Crew, Process, Task

import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODEL = "gemma3:4b"


def _build_crewai_llm() -> Any:
    """Build CrewAI LLM object if available, else fall back to provider string."""
    try:
        from crewai import LLM  # type: ignore

        return LLM(model=f"ollama/{MODEL}", base_url="http://localhost:11434")
    except Exception:
        return f"ollama/{MODEL}"


def build_release_crew() -> Crew:
    llm = _build_crewai_llm()

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

    crew = build_release_crew()
    cached_crew = CrewAICacheAdapter(crew, manager)

    inputs = {
        "release_context": (
            "Service: payments-api; change: retries + webhook async pipeline; "
            "traffic: 2.1M requests/day; known issue: timeout test instability."
        )
    }

    t0 = time.perf_counter()
    out1 = cached_crew.kickoff(inputs=inputs)
    t1 = time.perf_counter()
    print("=== First Run (full crew execution expected) ===")
    print(out1)
    print(f"Time: {t1 - t0:.3f}s")

    t2 = time.perf_counter()
    out2 = cached_crew.kickoff(inputs=inputs)
    t3 = time.perf_counter()
    print("\n=== Second Run (cache hit expected) ===")
    print(out2)
    print(f"Time: {t3 - t2:.3f}s  ({(t1 - t0) / (t3 - t2):.0f}x faster)")


if __name__ == "__main__":
    main()
