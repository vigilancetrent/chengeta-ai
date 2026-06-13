# A2A (Agent-to-Agent)

Cache inter-agent communication payloads with the framework-agnostic A2A adapter.
It wraps any callable that takes a payload and returns a response.

```bash
pip install a2a-sdk chengeta-ai
```

---

## 7.1 Basic process() call

Cache the result of a handler function so repeated calls with the same payload
skip the expensive downstream work.

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="a2a"),
)
adapter = A2ACacheAdapter(manager, agent_id="planner")

def planner_handler(task: dict) -> dict:
    # Expensive downstream call
    return {"plan": f"Steps to solve: {task['objective']}"}

payload = {"objective": "Build a recommendation system"}

result1 = adapter.process(planner_handler, payload)   # real call
result2 = adapter.process(planner_handler, payload)   # cache hit
assert result1 == result2
print(result1)
```

---

## 7.2 @wrap decorator

Use the `@adapter.wrap` decorator for a cleaner syntax.

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter

manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder())
adapter = A2ACacheAdapter(manager, agent_id="summarizer")

@adapter.wrap
def summarize(payload: dict) -> dict:
    text = payload["text"]
    # ... call LLM ...
    return {"summary": text[:100] + "..."}

payload = {"text": "Long document about vector databases..."}
print(summarize(payload))   # first call
print(summarize(payload))   # cache hit
```

---

## 7.3 Async aprocess()

Use `aprocess()` for async handler functions.

```python
import asyncio
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter

manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder())
adapter = A2ACacheAdapter(manager, agent_id="executor")

async def async_executor(payload: dict) -> dict:
    # Simulate async downstream agent call
    await asyncio.sleep(0.1)
    return {"result": f"executed: {payload['task']}"}

async def main():
    task = {"task": "analyze sentiment of customer reviews"}
    r1 = await adapter.aprocess(async_executor, task)
    r2 = await adapter.aprocess(async_executor, task)  # instant
    assert r1 == r2
    print(r1)

asyncio.run(main())
```

---

## 7.4 A2A with a2a-sdk 0.3.x TaskHandler

Integrate with the `a2a-sdk` `AgentExecutor` interface for standards-compliant agent services.

```python
# pip install a2a-sdk>=0.3
import asyncio
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Task, TaskState
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter

manager = CacheManager(
    backend=DiskBackend(directory="/var/cache/a2a"),
    key_builder=CacheKeyBuilder(namespace="a2a"),
)
adapter = A2ACacheAdapter(manager, agent_id="my-agent")

class CachedAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task
        payload = {"input": task.history[-1].parts[0].root.text if task.history else ""}

        async def _run(p: dict) -> dict:
            # Replace with actual model call
            return {"output": f"Answer to: {p['input']}"}

        result = await adapter.aprocess(_run, payload)
        await event_queue.enqueue_event(
            Task(id=task.id, contextId=task.contextId, state=TaskState.completed)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
```

---

## 7.5 Multi-agent pipeline with A2A caching

Chain multiple A2A-cached agents into a pipeline. On the second run every step
is served from cache.

```python
import asyncio
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, TTLPolicy
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="a2a"),
    ttl_policy=TTLPolicy(default_ttl=1800),
)

planner   = A2ACacheAdapter(manager, agent_id="planner")
executor  = A2ACacheAdapter(manager, agent_id="executor")
reviewer  = A2ACacheAdapter(manager, agent_id="reviewer")

async def plan(payload):   return {"plan": f"plan for {payload['goal']}"}
async def execute(payload): return {"result": f"done: {payload['plan']}"}
async def review(payload):  return {"review": f"looks good: {payload['result']}"}

async def pipeline(goal: str) -> dict:
    step1 = await planner.aprocess(plan, {"goal": goal})
    step2 = await executor.aprocess(execute, step1)
    step3 = await reviewer.aprocess(review, step2)
    return step3

asyncio.run(pipeline("Build a chatbot"))
asyncio.run(pipeline("Build a chatbot"))  # all three steps served from cache
```
