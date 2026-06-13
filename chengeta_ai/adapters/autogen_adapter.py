"""AutoGen cache adapter — supports both pyautogen 0.2.x and autogen-agentchat 0.4+."""

from __future__ import annotations

import json
import pickle
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from chengeta_ai.core.cache_manager import CacheManager

# autogen-agentchat 0.4+ (new API: autogen_agentchat.agents)
try:
    from autogen_agentchat.agents import (  # type: ignore[import-untyped]
        AssistantAgent,
        UserProxyAgent,
    )

    _AUTOGEN_V2 = True
except ImportError:
    AssistantAgent = None  # type: ignore[assignment,misc]
    UserProxyAgent = None  # type: ignore[assignment,misc]
    _AUTOGEN_V2 = False

# pyautogen 0.2.x / autogen 0.2 (legacy API: autogen.ConversableAgent)
try:
    from autogen import ConversableAgent  # type: ignore[import-untyped]

    _AUTOGEN_V1 = True
except ImportError:
    ConversableAgent = None  # type: ignore[assignment,misc]
    _AUTOGEN_V1 = False

_AUTOGEN_AVAILABLE = _AUTOGEN_V1 or _AUTOGEN_V2


class AutoGenCacheAdapter:
    """Wraps an AutoGen agent with reply caching.

    Supports both API generations:

    **autogen-agentchat 0.4+** (new API)::

        from autogen_agentchat.agents import AssistantAgent
        from autogen_agentchat.teams import RoundRobinGroupChat
        from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

        agent = AssistantAgent("assistant", model_client=...)
        cached = AutoGenCacheAdapter(agent, cache_manager)

        # Direct cached run_stream wrapper
        result = await cached.arun("What is 2+2?")

    **pyautogen 0.2.x** (legacy API)::

        from autogen import ConversableAgent
        from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

        agent = ConversableAgent(name="assistant", llm_config={...})
        cached = AutoGenCacheAdapter(agent, cache_manager)
        reply = cached.generate_reply(messages=[{"role": "user", "content": "Hi"}])

    Install with: pip install 'chengeta-ai[autogen]'
    """

    def __init__(self, agent: Any, cache_manager: "CacheManager") -> None:
        if not _AUTOGEN_AVAILABLE:
            raise ImportError(
                "AutoGenCacheAdapter requires 'autogen-agentchat' (v0.4+) or 'pyautogen' (v0.2.x). "
                "Install with:\n"
                "  pip install 'autogen-agentchat>=0.4'          # new API\n"
                "  pip install 'chengeta-ai[autogen]'            # legacy API"
            )
        self._agent = agent
        self._manager = cache_manager

        # Detect which API generation the wrapped agent uses
        self._is_v2 = _AUTOGEN_V2 and (
            AssistantAgent is not None
            and isinstance(agent, AssistantAgent)
            or UserProxyAgent is not None
            and isinstance(agent, UserProxyAgent)
        )

    # ------------------------------------------------------------------
    # Key builder helpers
    # ------------------------------------------------------------------

    def _key_from_messages(self, messages: list[Any]) -> str:
        payload = json.dumps(messages, sort_keys=True, default=str)
        agent_name = getattr(self._agent, "name", "agent")
        return self._manager.key_builder.build("response", payload, extra={"agent": agent_name})

    def _key_from_str(self, message: str, **kwargs: Any) -> str:
        agent_name = getattr(self._agent, "name", "agent")
        return self._manager.key_builder.build(
            "response",
            message,
            extra={"agent": agent_name, **{k: str(v) for k, v in kwargs.items()}},
        )

    # ------------------------------------------------------------------
    # pyautogen 0.2.x  (ConversableAgent.generate_reply)
    # ------------------------------------------------------------------

    def generate_reply(
        self,
        messages: list[dict[str, Any]] | None = None,
        sender: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Cached generate_reply for pyautogen 0.2.x agents."""
        msgs = messages or []
        key = self._key_from_messages(msgs)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301
        reply = self._agent.generate_reply(messages=msgs, sender=sender, **kwargs)
        if reply is not None:
            self._manager.set(key, pickle.dumps(reply), cache_type="response")
        return reply

    # ------------------------------------------------------------------
    # autogen-agentchat 0.4+  (AssistantAgent.run / run_stream)
    # ------------------------------------------------------------------

    async def arun(self, message: str, **kwargs: Any) -> Any:
        """Async cached run for autogen-agentchat 0.4+ agents.

        Wraps agent.run() — falls back to generate_reply for 0.2.x agents.
        """
        key = self._key_from_str(message, **kwargs)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301

        if hasattr(self._agent, "run"):
            result = await self._agent.run(task=message, **kwargs)
        else:
            # Fallback: v0.2.x agent — wrap message in list
            result = self._agent.generate_reply(
                messages=[{"role": "user", "content": message}], **kwargs
            )

        if result is not None:
            self._manager.set(key, pickle.dumps(result), cache_type="response")
        return result

    def run(self, message: str, **kwargs: Any) -> Any:
        """Sync cached run; delegates to generate_reply for v0.2.x agents."""
        key = self._key_from_str(message, **kwargs)
        raw = self._manager.get(key)
        if raw is not None:
            return pickle.loads(raw)  # noqa: S301

        if hasattr(self._agent, "run") and not self._is_v2:
            result = self._agent.run(task=message, **kwargs)
        else:
            result = self._agent.generate_reply(
                messages=[{"role": "user", "content": message}], **kwargs
            )

        if result is not None:
            self._manager.set(key, pickle.dumps(result), cache_type="response")
        return result

    # ------------------------------------------------------------------
    # Transparent proxy — any attribute not overridden passes through
    # ------------------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        return getattr(self._agent, name)
