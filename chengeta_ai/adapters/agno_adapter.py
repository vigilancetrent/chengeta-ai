"""Agno agent cache adapter."""

from __future__ import annotations

import pickle
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from chengeta_ai.core.cache_manager import CacheManager

try:
    from agno.agent import Agent  # type: ignore[import-untyped]

    _AGNO_AVAILABLE = True
except ImportError:
    Agent = None  # type: ignore[assignment]
    _AGNO_AVAILABLE = False


class AgnoCacheAdapter:
    """Wraps an Agno Agent with response caching.

    Intercepts ``run()`` and ``arun()`` to serve cached responses for
    identical messages/inputs.

    Usage::

        from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

        agent = Agent(model=..., tools=[...])
        cached = AgnoCacheAdapter(agent, cache_manager)
        response = cached.run("What is AI?")

    Install with: pip install 'chengeta-ai[agno]'
    """

    def __init__(self, agent: Any, cache_manager: "CacheManager") -> None:
        if not _AGNO_AVAILABLE:
            raise ImportError(
                "AgnoCacheAdapter requires 'agno'. Install with: pip install 'chengeta-ai[agno]'"
            )
        self._agent = agent
        self._manager = cache_manager

    def _key(self, message: Any, **kwargs: Any) -> str:
        return self._manager.key_builder.build(
            "response",
            str(message),
            extra={"type": "agno", **{k: str(v) for k, v in kwargs.items()}},
        )

    def run(self, message: Any, **kwargs: Any) -> Any:
        key = self._key(message, **kwargs)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301
        result = self._agent.run(message, **kwargs)
        self._manager.set(key, pickle.dumps(result), cache_type="response")
        return result

    async def arun(self, message: Any, **kwargs: Any) -> Any:
        key = self._key(message, **kwargs)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301
        result = await self._agent.arun(message, **kwargs)
        self._manager.set(key, pickle.dumps(result), cache_type="response")
        return result

    def __getattr__(self, name: str) -> Any:
        return getattr(self._agent, name)
