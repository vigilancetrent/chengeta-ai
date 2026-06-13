"""A2A (Agent-to-Agent) message cache adapter."""

from __future__ import annotations

import pickle
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from chengeta_ai.core.cache_manager import CacheManager


class A2ACacheAdapter:
    """Caches inter-agent message responses in A2A workflows.

    Framework-agnostic: wraps any callable that processes an agent task
    (message/payload in, response out). Compatible with Google A2A SDK and
    any custom A2A implementation.

    Usage::

        from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter

        adapter = A2ACacheAdapter(cache_manager, agent_id="planner")

        @adapter.wrap
        def handle_task(task_payload: dict) -> dict:
            return downstream_agent.process(task_payload)

    Args:
        cache_manager: CacheManager instance.
        agent_id: Identifier for the agent being wrapped (used in key).
    """

    def __init__(self, cache_manager: "CacheManager", agent_id: str = "default") -> None:
        self._manager = cache_manager
        self._agent_id = agent_id

    def _key(self, payload: Any) -> str:
        return self._manager.key_builder.build(
            "response", str(payload), extra={"agent": self._agent_id, "type": "a2a"}
        )

    def process(self, handler: Any, payload: Any, **kwargs: Any) -> Any:
        """Process a task, returning a cached result if available."""
        key = self._key(payload)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301
        result = handler(payload, **kwargs)
        self._manager.set(key, pickle.dumps(result), cache_type="response")
        return result

    async def aprocess(self, handler: Any, payload: Any, **kwargs: Any) -> Any:
        """Async version of process."""
        key = self._key(payload)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301
        result = await handler(payload, **kwargs)
        self._manager.set(key, pickle.dumps(result), cache_type="response")
        return result

    def wrap(self, handler_fn: Any) -> Any:
        """Decorator to wrap a task handler with caching."""
        import functools

        @functools.wraps(handler_fn)
        def wrapper(payload: Any, **kwargs: Any) -> Any:
            return self.process(handler_fn, payload, **kwargs)

        return wrapper
