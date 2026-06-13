"""LangGraph checkpoint adapter — compatible with langgraph >=0.1, >=1.x."""

from __future__ import annotations

import builtins
import pickle
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from chengeta_ai.core.cache_manager import CacheManager

# langgraph 1.x changed the saver interface significantly.
# We import what's available and fall back gracefully.
try:
    from langgraph.checkpoint.base import (  # type: ignore[import-untyped]
        BaseCheckpointSaver,
        CheckpointTuple,
    )

    try:
        # langgraph >=1.0 — new_versions param required on put()
        from langgraph.checkpoint.base import ChannelVersions  # type: ignore[import-untyped]  # noqa: F401

        _LG_V1 = True
    except ImportError:
        _LG_V1 = False

    _LANGGRAPH_AVAILABLE = True
except ImportError:
    BaseCheckpointSaver = object  # type: ignore[assignment,misc]
    CheckpointTuple = None  # type: ignore[assignment,misc]
    _LG_V1 = False
    _LANGGRAPH_AVAILABLE = False


class LangGraphCacheAdapter(BaseCheckpointSaver):  # type: ignore[misc]
    """Implements LangGraph BaseCheckpointSaver using chengeta_ai.

    Persists LangGraph state-graph checkpoints in any chengeta-ai backend
    (in-memory, disk, Redis). Compatible with langgraph >=0.1 and >=1.0.

    langgraph 0.x usage::

        from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter

        saver = LangGraphCacheAdapter(cache_manager)
        graph = StateGraph(...).compile(checkpointer=saver)
        result = graph.invoke(input, config={"configurable": {"thread_id": "t1"}})

    langgraph 1.x usage (same API — adapter detects version automatically)::

        saver = LangGraphCacheAdapter(cache_manager)
        graph = StateGraph(...).compile(checkpointer=saver)

    Install with: pip install 'chengeta-ai[langgraph]'
    """

    def __init__(self, cache_manager: "CacheManager") -> None:
        if not _LANGGRAPH_AVAILABLE:
            raise ImportError(
                "LangGraphCacheAdapter requires 'langgraph'. "
                "Install with: pip install 'chengeta-ai[langgraph]'"
            )
        super().__init__()
        self._manager = cache_manager

    # ------------------------------------------------------------------
    # Key helpers
    # ------------------------------------------------------------------

    def _key(self, thread_id: str, checkpoint_ns: str = "", checkpoint_id: str = "") -> str:
        return self._manager.key_builder.build(
            "context",
            thread_id,
            extra={"ns": checkpoint_ns, "cid": checkpoint_id, "type": "lg_checkpoint"},
        )

    def _thread_list_key(self, thread_id: str) -> str:
        return self._manager.key_builder.build(
            "context", thread_id, extra={"type": "lg_thread_index"}
        )

    def _config_parts(self, config: dict[str, Any]) -> tuple[str, str, str]:
        cfg = config.get("configurable", {})
        thread_id: str = cfg.get("thread_id", "default")
        checkpoint_ns: str = cfg.get("checkpoint_ns", "")
        checkpoint_id: str = cfg.get("checkpoint_id", "")
        return thread_id, checkpoint_ns, checkpoint_id

    # ------------------------------------------------------------------
    # langgraph 0.x interface  (get / put / list)
    # ------------------------------------------------------------------

    def get(self, config: dict[str, Any]) -> Any | None:  # type: ignore[override]
        """Return raw checkpoint dict (langgraph 0.x compat)."""
        thread_id, ns, cid = self._config_parts(config)
        raw = self._manager.get(self._key(thread_id, ns, cid))
        if raw is None:
            return None
        stored = pickle.loads(raw)  # noqa: S301
        return stored.get("checkpoint")

    # ------------------------------------------------------------------
    # langgraph 1.x interface  (get_tuple / put / put_writes / list)
    # ------------------------------------------------------------------

    def get_tuple(self, config: dict[str, Any]) -> Any | None:
        """Return CheckpointTuple (langgraph 1.x)."""
        thread_id, ns, cid = self._config_parts(config)

        # If no checkpoint_id given, load the latest one for this thread
        if not cid:
            index_raw = self._manager.get(self._thread_list_key(thread_id))
            if index_raw is None:
                return None
            index: list[str] = pickle.loads(index_raw)  # noqa: S301
            if not index:
                return None
            cid = index[-1]

        raw = self._manager.get(self._key(thread_id, ns, cid))
        if raw is None:
            return None
        stored = pickle.loads(raw)  # noqa: S301

        if CheckpointTuple is None:
            return stored

        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": ns,
                    "checkpoint_id": cid,
                }
            },
            checkpoint=stored.get("checkpoint", {}),
            metadata=stored.get("metadata", {}),
            parent_config=stored.get("parent_config"),
            pending_writes=stored.get("pending_writes"),
        )

    def put(  # type: ignore[override]
        self,
        config: dict[str, Any],
        checkpoint: Any,
        metadata: Any,
        new_versions: Any = None,  # langgraph 1.x passes ChannelVersions here
    ) -> dict[str, Any]:
        """Store a checkpoint; returns the config with checkpoint_id filled in."""
        thread_id, ns, cid = self._config_parts(config)

        # Generate checkpoint_id from metadata if not present (langgraph 1.x)
        import time as _time

        if not cid:
            cid = str(_time.monotonic_ns())

        key = self._key(thread_id, ns, cid)
        self._manager.set(
            key,
            pickle.dumps(
                {
                    "checkpoint": checkpoint,
                    "metadata": metadata,
                    "parent_config": config,
                    "pending_writes": None,
                    "new_versions": new_versions,
                }
            ),
            tags=[f"thread:{thread_id}"],
        )

        # Update thread index
        index_raw = self._manager.get(self._thread_list_key(thread_id))
        index: list[str] = pickle.loads(index_raw) if index_raw else []  # noqa: S301
        if cid not in index:
            index.append(cid)
        self._manager.set(self._thread_list_key(thread_id), pickle.dumps(index))

        return {
            **config,
            "configurable": {
                **config.get("configurable", {}),
                "checkpoint_id": cid,
                "thread_id": thread_id,
                "checkpoint_ns": ns,
            },
        }

    def put_writes(
        self,
        config: dict[str, Any],
        writes: list[tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Store intermediate writes for a checkpoint (langgraph 1.x)."""
        thread_id, ns, cid = self._config_parts(config)
        writes_key = self._manager.key_builder.build(
            "context",
            thread_id,
            extra={"ns": ns, "cid": cid, "task": task_id, "type": "lg_writes"},
        )
        self._manager.set(writes_key, pickle.dumps(writes))

    def list(  # type: ignore[override]
        self,
        config: dict[str, Any],
        *,
        filter: dict[str, Any] | None = None,  # noqa: A002
        before: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> Iterator[Any]:
        """Yield CheckpointTuples for a thread (most recent first)."""
        thread_id, ns, _ = self._config_parts(config)
        index_raw = self._manager.get(self._thread_list_key(thread_id))
        if index_raw is None:
            return
        index: list[str] = pickle.loads(index_raw)  # noqa: S301
        count = 0
        for cid in reversed(index):
            if limit is not None and count >= limit:
                break
            result = self.get_tuple(
                {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": ns,
                        "checkpoint_id": cid,
                    }
                }
            )
            if result is not None:
                yield result
                count += 1

    # ------------------------------------------------------------------
    # Async shims (delegate to sync — use AsyncLangGraphCacheAdapter for
    # true async if your backend supports it)
    # ------------------------------------------------------------------

    async def aget_tuple(self, config: dict[str, Any]) -> Any | None:
        return self.get_tuple(config)

    async def aput(
        self,
        config: dict[str, Any],
        checkpoint: Any,
        metadata: Any,
        new_versions: Any = None,
    ) -> dict[str, Any]:
        return self.put(config, checkpoint, metadata, new_versions)

    async def aput_writes(
        self,
        config: dict[str, Any],
        writes: builtins.list[tuple[str, Any]],
        task_id: str,
    ) -> None:
        self.put_writes(config, writes, task_id)

    async def alist(  # type: ignore[override]
        self,
        config: dict[str, Any],
        *,
        filter: dict[str, Any] | None = None,  # noqa: A002
        before: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> Any:
        for item in self.list(config, filter=filter, before=before, limit=limit):  # type: ignore[arg-type]
            yield item

    def get_next_version(self, current: Any, channel: Any) -> Any:
        """Return the next channel version (langgraph 1.x)."""
        if current is None:
            return 1
        if isinstance(current, int):
            return current + 1
        return str(int(current) + 1)
