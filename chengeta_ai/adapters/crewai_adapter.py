"""CrewAI task output cache adapter."""

from __future__ import annotations

import pickle
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from chengeta_ai.core.cache_manager import CacheManager

try:
    from crewai import Crew  # type: ignore[import-untyped]

    _CREWAI_AVAILABLE = True
except ImportError:
    Crew = None  # type: ignore[assignment]
    _CREWAI_AVAILABLE = False


class CrewAICacheAdapter:
    """Wraps a CrewAI Crew with task output caching.

    Intercepts ``kickoff()`` to cache the final crew output keyed by inputs.
    Avoids re-executing the entire crew pipeline for identical input sets.

    Usage::

        from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

        crew = Crew(agents=[...], tasks=[...])
        cached_crew = CrewAICacheAdapter(crew, cache_manager)
        result = cached_crew.kickoff(inputs={"topic": "AI"})

    Install with: pip install 'chengeta-ai[crewai]'
    """

    def __init__(self, crew: Any, cache_manager: "CacheManager") -> None:
        if not _CREWAI_AVAILABLE:
            raise ImportError(
                "CrewAICacheAdapter requires 'crewai'. "
                "Install with: pip install 'chengeta-ai[crewai]'"
            )
        self._crew = crew
        self._manager = cache_manager

    def _key(self, inputs: dict[str, Any] | None) -> str:
        return self._manager.key_builder.build(
            "response", inputs or {}, extra={"type": "crewai_kickoff"}
        )

    def kickoff(self, inputs: dict[str, Any] | None = None) -> Any:
        key = self._key(inputs)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301
        result = self._crew.kickoff(inputs=inputs)
        self._manager.set(key, pickle.dumps(result), cache_type="response")
        return result

    async def kickoff_async(self, inputs: dict[str, Any] | None = None) -> Any:
        key = self._key(inputs)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301
        result = await self._crew.kickoff_async(inputs=inputs)
        self._manager.set(key, pickle.dumps(result), cache_type="response")
        return result

    def __getattr__(self, name: str) -> Any:
        return getattr(self._crew, name)
