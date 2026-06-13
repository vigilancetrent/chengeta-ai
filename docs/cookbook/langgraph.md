# LangGraph

Use chengeta-ai as a LangGraph checkpointer for persistent, resumable state graphs.
The adapter auto-detects the LangGraph API version (0.1 and 1.x).

```bash
pip install 'chengeta-ai[langgraph]'
```

---

## 3.1 State graph with in-memory checkpointer

Wire chengeta-ai as the LangGraph checkpointer so graph state is persisted between invocations.

```python
from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOpenAI(model="gpt-4o-mini")

def chatbot(state: State) -> State:
    return {"messages": [llm.invoke(state["messages"])]}

builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.set_entry_point("chatbot")
builder.add_edge("chatbot", END)

# Wire chengeta-ai as the checkpointer
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="lg"),
)
checkpointer = LangGraphCacheAdapter(manager)
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "session-1"}}

result = graph.invoke({"messages": [("user", "What is 2+2?")]}, config=config)
print(result["messages"][-1].content)

# Resume the same thread — state is loaded from chengeta
result2 = graph.invoke({"messages": [("user", "What did I just ask?")]}, config=config)
print(result2["messages"][-1].content)
```

---

## 3.2 Persistent checkpointer with disk backend

Use a disk backend so graph state survives process restarts.

```python
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter

manager = CacheManager(
    backend=DiskBackend(directory="/var/cache/langgraph"),
    key_builder=CacheKeyBuilder(namespace="lg"),
)
checkpointer = LangGraphCacheAdapter(manager)

# graph = builder.compile(checkpointer=checkpointer)
# State survives process restarts — same thread_id resumes the conversation
```

---

## 3.3 List checkpoint history for a thread

Retrieve the most recent checkpoints for a given thread.

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter

manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder())
checkpointer = LangGraphCacheAdapter(manager)

config = {"configurable": {"thread_id": "session-1"}}

# After running several graph steps:
for checkpoint in checkpointer.list(config, limit=5):
    print(checkpoint)
```

---

## 3.4 Multi-agent graph with shared cache

Both LLM response caching and graph state checkpointing share a single `CacheManager`.

```python
from langgraph.graph import StateGraph, END
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter
from langchain_core.globals import set_llm_cache
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

# Both LLM cache and graph checkpoints share one manager
manager = CacheManager(
    backend=DiskBackend(directory="/var/cache/multi_agent"),
    key_builder=CacheKeyBuilder(namespace="ma"),
)
set_llm_cache(LangChainCacheAdapter(manager))   # cache all LLM calls
checkpointer = LangGraphCacheAdapter(manager)   # cache graph state

class State(TypedDict):
    messages: Annotated[list, add_messages]
    draft: str

planner = ChatOpenAI(model="gpt-4o", temperature=0)
writer  = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

def plan(state: State) -> State:
    plan_msg = planner.invoke([
        {"role": "system", "content": "Create a numbered outline."},
        *state["messages"],
    ])
    return {"draft": plan_msg.content}

def write(state: State) -> State:
    write_msg = writer.invoke([
        {"role": "system", "content": "Expand the outline into prose."},
        {"role": "user",   "content": state["draft"]},
    ])
    return {"messages": [write_msg]}

g = StateGraph(State)
g.add_node("plan",  plan)
g.add_node("write", write)
g.set_entry_point("plan")
g.add_edge("plan", "write")
g.add_edge("write", END)

graph = g.compile(checkpointer=checkpointer)
result = graph.invoke(
    {"messages": [("user", "Write a short blog post about vector caching.")]},
    config={"configurable": {"thread_id": "blog-001"}},
)
print(result["messages"][-1].content)
```
