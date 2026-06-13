# chengeta-ai Cookbook

Practical, runnable examples for every supported AI framework.
Each chapter is self-contained — copy any recipe straight into your project.

**Framework versions tested:**

| Framework | Package | Tested version |
|---|---|---|
| LangChain | `langchain-core` | ≥ 0.2, 1.x |
| LangGraph | `langgraph` | ≥ 0.1, 1.x |
| AutoGen (new) | `autogen-agentchat` | ≥ 0.4, 0.7.x |
| AutoGen (legacy) | `pyautogen` | 0.2.x |
| CrewAI | `crewai` | ≥ 0.28, 1.x |
| Agno | `agno` | ≥ 0.1, 2.x |
| A2A | `a2a-sdk` | ≥ 0.2, 0.3.x |

---

## Table of Contents

1. [Core Setup](#1-core-setup)
2. [LangChain](#2-langchain)
3. [LangGraph](#3-langgraph)
4. [AutoGen](#4-autogen)
5. [CrewAI](#5-crewai)
6. [Agno](#6-agno)
7. [A2A (Agent-to-Agent)](#7-a2a-agent-to-agent)
8. [Semantic Cache](#8-semantic-cache)
9. [Redis Backend](#9-redis-backend)
10. [Tag-Based Invalidation](#10-tag-based-invalidation)
11. [TTL Policies](#11-ttl-policies)
12. [Multi-Framework Pipeline](#12-multi-framework-pipeline)

---

## 1. Core Setup

### 1.1 In-memory cache (zero config)

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder

manager = CacheManager(
    backend=InMemoryBackend(max_size=10_000),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)
```

### 1.2 Disk cache (survives process restarts)

```python
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder

manager = CacheManager(
    backend=DiskBackend(path="/var/cache/myapp"),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)
```

### 1.3 From environment variables

```bash
export CHENGETA_BACKEND=redis
export CHENGETA_REDIS_URL=redis://localhost:6379/0
export CHENGETA_DEFAULT_TTL=3600
export CHENGETA_NAMESPACE=myapp
```

```python
from chengeta_ai import CacheManager, ChengetaSettings

manager = CacheManager.from_settings(ChengetaSettings.from_env())
```

### 1.4 With full TTL policy per layer

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, TTLPolicy

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="myapp"),
    ttl_policy=TTLPolicy(
        default_ttl=3600,
        per_type={
            "embed": 86_400,      # embeddings last 24 h
            "retrieval": 3_600,   # retrieval results last 1 h
            "context": 1_800,     # session context 30 min
            "response": 600,      # LLM responses 10 min
        },
    ),
)
```

### 1.5 With tag-based invalidation

```python
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder, InvalidationEngine
)

tag_store = InMemoryBackend()
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="myapp"),
    invalidation_engine=InvalidationEngine(tag_store),
)
```

---

## 2. LangChain

**Install:** `pip install 'chengeta-ai[langchain]'`

### 2.1 Drop-in global LLM cache

Register once at app startup — every `ChatOpenAI` / `ChatAnthropic` call is
automatically cached.

```python
from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="lc"),
)
set_llm_cache(LangChainCacheAdapter(manager))

llm = ChatOpenAI(model="gpt-4o")

# First call — hits OpenAI
response1 = llm.invoke("What is the capital of France?")

# Second call — served from cache, 0 tokens used
response2 = llm.invoke("What is the capital of France?")

assert response1.content == response2.content
print("Cache working:", response1.content)
```

### 2.2 Per-chain cache with disk backend

```python
from langchain_core.globals import set_llm_cache
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

# Persistent cache — survives server restarts
manager = CacheManager(
    backend=DiskBackend(path="/var/cache/langchain"),
    key_builder=CacheKeyBuilder(namespace="lc"),
)
set_llm_cache(LangChainCacheAdapter(manager))

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini")

result = chain.invoke({"question": "Explain RAG in one sentence."})
print(result.content)
```

### 2.3 Async chain with cached embeddings

```python
import asyncio
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.globals import set_llm_cache
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, EmbeddingCache
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="lc"),
)
set_llm_cache(LangChainCacheAdapter(manager))
emb_cache = EmbeddingCache(manager)

embedder = OpenAIEmbeddings(model="text-embedding-3-small")

async def get_embedding(text: str):
    return emb_cache.get_or_compute(
        text=text,
        compute_fn=lambda t: embedder.embed_query(t),
        model_id="text-embedding-3-small",
    )

async def main():
    vec1 = await get_embedding("What is machine learning?")
    vec2 = await get_embedding("What is machine learning?")  # from cache
    assert (vec1 == vec2).all()
    print("Embedding cache hit confirmed, shape:", vec1.shape)

asyncio.run(main())
```

### 2.4 ResponseCache + LangChain LLMMiddleware together

```python
from langchain_openai import ChatOpenAI
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    ResponseCache, LLMMiddleware,
)

manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder())
cache = ResponseCache(manager)
key_builder = CacheKeyBuilder(namespace="lc")

# Wrap the raw LLM function with middleware
middleware = LLMMiddleware(cache, key_builder, model_id="gpt-4o")

@middleware
def call_llm(messages: list[dict]) -> str:
    llm = ChatOpenAI(model="gpt-4o")
    return llm.invoke(messages).content

messages = [{"role": "user", "content": "Name three planets."}]
print(call_llm(messages))   # API call
print(call_llm(messages))   # Cache hit — instant
```

### 2.5 Cache invalidation by model

```python
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    InvalidationEngine, ResponseCache,
)
from langchain_core.globals import set_llm_cache
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

tag_store = InMemoryBackend()
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="lc"),
    invalidation_engine=InvalidationEngine(tag_store),
)
set_llm_cache(LangChainCacheAdapter(manager))
rc = ResponseCache(manager)

messages = [{"role": "user", "content": "Hello"}]
rc.set(messages, "Hi there!", "gpt-4o", tags=["model:gpt-4o"])

# Invalidate everything cached for gpt-4o
count = rc.invalidate_model("gpt-4o")
print(f"Invalidated {count} cache entries for gpt-4o")
```

---

## 3. LangGraph

**Install:** `pip install 'chengeta-ai[langgraph]'`

Compatible with langgraph ≥ 0.1 and ≥ 1.0 — the adapter auto-detects the API version.

### 3.1 State graph with in-memory checkpointer

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

### 3.2 Persistent checkpointer with disk backend

```python
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter

manager = CacheManager(
    backend=DiskBackend(path="/var/cache/langgraph"),
    key_builder=CacheKeyBuilder(namespace="lg"),
)
checkpointer = LangGraphCacheAdapter(manager)

# graph = builder.compile(checkpointer=checkpointer)
# State survives process restarts — same thread_id resumes the conversation
```

### 3.3 List checkpoint history for a thread

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

### 3.4 Multi-agent graph with shared cache

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
    backend=DiskBackend(path="/var/cache/multi_agent"),
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

---

## 4. AutoGen

**Install (new API):**    `pip install 'autogen-agentchat>=0.4'`
**Install (legacy API):** `pip install 'chengeta-ai[autogen]'`

### 4.1 autogen-agentchat 0.4+ — AssistantAgent with async caching

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="ag"),
)

model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
agent = AssistantAgent("assistant", model_client=model_client)
cached = AutoGenCacheAdapter(agent, manager)

async def main():
    # First call — hits the model
    result1 = await cached.arun("What is the speed of light?")
    # Second call — instant cache hit
    result2 = await cached.arun("What is the speed of light?")
    print("Same result:", result1 == result2)

asyncio.run(main())
```

### 4.2 autogen-agentchat 0.4+ — RoundRobinGroupChat with cached agents

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=DiskBackend(path="/var/cache/autogen"),
    key_builder=CacheKeyBuilder(namespace="ag"),
)
client = OpenAIChatCompletionClient(model="gpt-4o-mini")

# Wrap each agent independently
researcher = AutoGenCacheAdapter(
    AssistantAgent("researcher", model_client=client,
                   system_message="Research and provide facts."),
    manager,
)
summarizer = AutoGenCacheAdapter(
    AssistantAgent("summarizer", model_client=client,
                   system_message="Summarize concisely."),
    manager,
)

async def main():
    team = RoundRobinGroupChat(
        [researcher._agent, summarizer._agent],  # pass inner agents to team
        termination_condition=MaxMessageTermination(4),
    )
    result = await team.run(task="Explain transformer attention in 3 sentences.")
    print(result.messages[-1].content)

asyncio.run(main())
```

### 4.3 pyautogen 0.2.x — ConversableAgent (legacy)

```python
from autogen import ConversableAgent, UserProxyAgent
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="ag-legacy"),
)

assistant = ConversableAgent(
    name="assistant",
    llm_config={"config_list": [{"model": "gpt-4o-mini", "api_key": "..."}]},
    system_message="You are a helpful assistant.",
)
cached_assistant = AutoGenCacheAdapter(assistant, manager)

messages = [{"role": "user", "content": "What is 10 * 10?"}]

reply1 = cached_assistant.generate_reply(messages)  # API call
reply2 = cached_assistant.generate_reply(messages)  # Cache hit

assert reply1 == reply2
print(reply1)
```

### 4.4 AutoGen + LangChain embeddings cached together

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_openai import OpenAIEmbeddings
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    EmbeddingCache, TTLPolicy,
)
from chengeta_ai.adapters.autogen_adapter import AutoGenCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="combo"),
    ttl_policy=TTLPolicy(default_ttl=3600, per_type={"embed": 86400}),
)
emb_cache  = EmbeddingCache(manager)
embedder   = OpenAIEmbeddings(model="text-embedding-3-small")
agent      = AssistantAgent("assistant", model_client=OpenAIChatCompletionClient(model="gpt-4o-mini"))
cached_agent = AutoGenCacheAdapter(agent, manager)

async def main():
    # Cache embeddings for retrieval context
    vec = emb_cache.get_or_compute(
        "transformer attention mechanism",
        lambda t: embedder.embed_query(t),
        model_id="text-embedding-3-small",
    )
    print("Embedding shape:", vec.shape)

    # Cache agent replies
    reply = await cached_agent.arun("What is the transformer attention mechanism?")
    print("Agent:", reply)

asyncio.run(main())
```

---

## 5. CrewAI

**Install:** `pip install 'chengeta-ai[crewai]'`

### 5.1 Basic crew with cached kickoff

```python
from crewai import Agent, Task, Crew, Process
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="crew"),
)

researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments in AI",
    backstory="You have 10 years of experience analyzing AI research papers.",
    verbose=True,
)
writer = Agent(
    role="Tech Content Strategist",
    goal="Create engaging tech content",
    backstory="You craft clear, compelling tech articles.",
    verbose=True,
)

research_task = Task(
    description="Research the latest trends in vector databases for AI.",
    expected_output="A bullet-point summary of 5 key trends.",
    agent=researcher,
)
write_task = Task(
    description="Write a 3-paragraph blog post based on the research.",
    expected_output="A complete blog post.",
    agent=writer,
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True,
)
cached_crew = CrewAICacheAdapter(crew, manager)

# First run — executes the full pipeline
result = cached_crew.kickoff(inputs={"topic": "vector databases"})
print(result)

# Second run with identical inputs — returned instantly from cache
result2 = cached_crew.kickoff(inputs={"topic": "vector databases"})
assert result == result2
```

### 5.2 Async crew kickoff

```python
import asyncio
from crewai import Agent, Task, Crew
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

manager = CacheManager(
    backend=DiskBackend(path="/var/cache/crew"),
    key_builder=CacheKeyBuilder(namespace="crew"),
)

# ... (define agents, tasks, crew as above)

async def main():
    cached_crew = CrewAICacheAdapter(crew, manager)
    result = await cached_crew.kickoff_async(inputs={"topic": "LLM fine-tuning"})
    print(result)

asyncio.run(main())
```

### 5.3 Cache invalidation after crew re-training

```python
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    InvalidationEngine,
)
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

tag_store = InMemoryBackend()
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="crew"),
    invalidation_engine=InvalidationEngine(tag_store),
)

cached_crew = CrewAICacheAdapter(crew, manager)

# Run with explicit tagging
key = manager.key_builder.build("response", {"topic": "AI"}, extra={"type": "crewai_kickoff"})
manager.set(key, b"old_result", tags=["crew:research_v1"])

# After re-training agents, invalidate the old cache
count = manager.invalidate("crew:research_v1")
print(f"Invalidated {count} stale crew results")
```

### 5.4 Crew + retrieval cache for knowledge base

```python
from crewai import Agent, Task, Crew
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, RetrievalCache
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="crew"),
)
ret_cache = RetrievalCache(manager)

def search_knowledge_base(query: str) -> list[dict]:
    """Retrieves docs — cached after first call."""
    return ret_cache.get_or_retrieve(
        query=query,
        retrieve_fn=lambda q: vectorstore.similarity_search(q, k=5),
        retriever_id="company-kb",
        top_k=5,
    )

# Inject the cached retriever into an agent tool
from crewai_tools import tool

@tool("Knowledge Base Search")
def kb_search(query: str) -> str:
    docs = search_knowledge_base(query)
    return "\n".join(d["content"] for d in docs)

researcher = Agent(
    role="Researcher",
    goal="Find relevant information",
    backstory="Expert researcher",
    tools=[kb_search],
)
```

---

## 6. Agno

**Install:** `pip install 'chengeta-ai[agno]'`

### 6.1 Single agent with sync caching

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="agno"),
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    description="You are a helpful assistant.",
    markdown=True,
)
cached = AgnoCacheAdapter(agent, manager)

# First call — hits the model
response1 = cached.run("Explain vector embeddings in 2 sentences.")
# Second call — instant cache hit
response2 = cached.run("Explain vector embeddings in 2 sentences.")

print(response1.content)
```

### 6.2 Async agent

```python
import asyncio
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="agno"),
)
agent = Agent(model=OpenAIChat(id="gpt-4o"), markdown=True)
cached = AgnoCacheAdapter(agent, manager)

async def main():
    r1 = await cached.arun("What year was Python created?")
    r2 = await cached.arun("What year was Python created?")  # cache hit
    print(r1.content)

asyncio.run(main())
```

### 6.3 Team of cached agents

```python
import asyncio
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

manager = CacheManager(
    backend=DiskBackend(path="/var/cache/agno"),
    key_builder=CacheKeyBuilder(namespace="agno"),
)

coder   = AgnoCacheAdapter(Agent(model=OpenAIChat(id="gpt-4o"), role="Write Python code"), manager)
tester  = AgnoCacheAdapter(Agent(model=OpenAIChat(id="gpt-4o-mini"), role="Write tests"), manager)

async def main():
    code    = await coder.arun("Write a function that computes Fibonacci numbers.")
    tests   = await tester.arun(f"Write pytest tests for:\n{code.content}")
    print("Code:\n", code.content)
    print("Tests:\n", tests.content)

asyncio.run(main())
```

### 6.4 Agno agent with tool calls — cache at tool level

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, RetrievalCache
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

manager = CacheManager(backend=InMemoryBackend(), key_builder=CacheKeyBuilder())
ret_cache = RetrievalCache(manager)

# Cache search results so repeated queries skip the web call
def cached_search(query: str) -> list[str]:
    def do_search(q: str) -> list[str]:
        return DuckDuckGoTools().search(q)

    return ret_cache.get_or_retrieve(
        query=query,
        retrieve_fn=do_search,
        retriever_id="duckduckgo",
        top_k=5,
    )

agent = Agent(model=OpenAIChat(id="gpt-4o-mini"), tools=[DuckDuckGoTools()])
cached_agent = AgnoCacheAdapter(agent, manager)

response = cached_agent.run("Latest news about AI regulation in 2025")
print(response.content)
```

### 6.5 Context cache for multi-turn sessions

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    ContextCache, InvalidationEngine,
)
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter

tag_store = InMemoryBackend()
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="agno"),
    invalidation_engine=InvalidationEngine(tag_store),
)
ctx_cache = ContextCache(manager)
agent = Agent(model=OpenAIChat(id="gpt-4o-mini"))
cached = AgnoCacheAdapter(agent, manager)

SESSION = "user-42"

# Store turns in context cache
ctx_cache.set(SESSION, 0, [{"role": "user", "content": "My name is Alice."}])
ctx_cache.set(SESSION, 1, [{"role": "assistant", "content": "Hello Alice!"}])

# Retrieve history
history = ctx_cache.get(SESSION, 0)
print("History:", history)

# End of session — clear context
ctx_cache.invalidate_session(SESSION)
```

---

## 7. A2A (Agent-to-Agent)

**Install:** `pip install a2a-sdk chengeta-ai`

The A2A adapter is framework-agnostic — it wraps any callable that takes a payload and returns a response.

### 7.1 Basic process() call

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

### 7.2 @wrap decorator

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

### 7.3 Async aprocess()

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

### 7.4 A2A with a2a-sdk 0.3.x TaskHandler

```python
# pip install a2a-sdk>=0.3
import asyncio
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Task, TaskState
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter

manager = CacheManager(
    backend=DiskBackend(path="/var/cache/a2a"),
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

### 7.5 Multi-agent pipeline with A2A caching

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

---

## 8. Semantic Cache

**Install:** `pip install 'chengeta-ai[vector-faiss]'`

Returns cached answers for semantically similar queries — not just exact matches.

### 8.1 Standalone semantic cache

```python
import numpy as np
from chengeta_ai import SemanticCache
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.backends.vector_backend import FAISSBackend

# Provide your own embed function (wraps any embedder)
from langchain_openai import OpenAIEmbeddings
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

def embed(text: str) -> np.ndarray:
    return np.array(embedder.embed_query(text), dtype=np.float32)

cache = SemanticCache(
    exact_backend=InMemoryBackend(),
    vector_backend=FAISSBackend(dim=1536),
    embed_fn=embed,
    threshold=0.93,   # cosine similarity cutoff
)

# Populate
cache.set("What is the capital of France?", "Paris")
cache.set("Who wrote Hamlet?", "William Shakespeare")

# Exact match
print(cache.get("What is the capital of France?"))   # "Paris"

# Semantically similar — still hits
print(cache.get("What's France's capital city?"))     # "Paris"
print(cache.get("Which city is the capital of France?"))  # "Paris"

# Unrelated — cache miss
print(cache.get("What is the speed of light?"))       # None
```

### 8.2 Semantic cache inside a LangChain chain

```python
import numpy as np
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from chengeta_ai import SemanticCache
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.backends.vector_backend import FAISSBackend

embedder = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini")

sem_cache = SemanticCache(
    exact_backend=InMemoryBackend(),
    vector_backend=FAISSBackend(dim=1536),
    embed_fn=lambda t: np.array(embedder.embed_query(t), dtype=np.float32),
    threshold=0.95,
)

def cached_ask(question: str) -> str:
    cached = sem_cache.get(question)
    if cached is not None:
        print("[CACHE HIT]")
        return cached
    answer = llm.invoke(question).content
    sem_cache.set(question, answer)
    return answer

print(cached_ask("What is RAG?"))
print(cached_ask("Can you explain RAG?"))          # hit
print(cached_ask("Describe retrieval augmented generation."))  # hit
```

### 8.3 Semantic cache with ChromaDB backend

```python
# pip install 'chengeta-ai[vector-chroma]'
import numpy as np
from chengeta_ai import SemanticCache
from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.backends.vector_backend import ChromaBackend

cache = SemanticCache(
    exact_backend=InMemoryBackend(),
    vector_backend=ChromaBackend(collection_name="qa_cache", dim=1536),
    embed_fn=lambda t: np.random.rand(1536).astype(np.float32),  # replace with real embedder
    threshold=0.92,
)
cache.set("Explain transformers", "Transformers are a type of neural network...")
print(cache.get("What are transformers?"))
```

---

## 9. Redis Backend

**Install:** `pip install 'chengeta-ai[redis]'`

### 9.1 Shared cache across multiple processes

```python
from chengeta_ai import CacheManager, CacheKeyBuilder
from chengeta_ai.backends.redis_backend import RedisBackend

manager = CacheManager(
    backend=RedisBackend(url="redis://localhost:6379/0", key_prefix="myapp:"),
    key_builder=CacheKeyBuilder(namespace="myapp"),
)

# Works identically to InMemoryBackend — but shared across processes
manager.set("my_key", {"result": 42}, ttl=300)
print(manager.get("my_key"))
```

### 9.2 Redis + LangChain

```python
from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI
from chengeta_ai import CacheManager, CacheKeyBuilder
from chengeta_ai.backends.redis_backend import RedisBackend
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter

manager = CacheManager(
    backend=RedisBackend(url="redis://localhost:6379/1"),
    key_builder=CacheKeyBuilder(namespace="lc"),
)
set_llm_cache(LangChainCacheAdapter(manager))

llm = ChatOpenAI(model="gpt-4o")
# All workers sharing this Redis instance will benefit from the same cache
print(llm.invoke("What is 2+2?").content)
```

### 9.3 Redis + CrewAI with TTL

```python
from chengeta_ai import CacheManager, CacheKeyBuilder, TTLPolicy
from chengeta_ai.backends.redis_backend import RedisBackend
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

manager = CacheManager(
    backend=RedisBackend(url="redis://localhost:6379/2"),
    key_builder=CacheKeyBuilder(namespace="crew"),
    ttl_policy=TTLPolicy(default_ttl=7200),  # 2-hour cache
)

cached_crew = CrewAICacheAdapter(crew, manager)
result = cached_crew.kickoff(inputs={"topic": "AI safety"})
```

---

## 10. Tag-Based Invalidation

Invalidate related cache entries in one call — by model, session, agent, or custom tag.

### 10.1 Invalidate all entries for a model

```python
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    InvalidationEngine, ResponseCache,
)

tag_store = InMemoryBackend()
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="inv"),
    invalidation_engine=InvalidationEngine(tag_store),
)
rc = ResponseCache(manager)

msgs = [{"role": "user", "content": "Hello"}]
rc.set(msgs, "Hi!",   model_id="gpt-4o",    tags=["model:gpt-4o"])
rc.set(msgs, "Hey!",  model_id="gpt-4o",    tags=["model:gpt-4o"])
rc.set(msgs, "Hola!", model_id="gpt-4o-mini", tags=["model:gpt-4o-mini"])

# Invalidate only gpt-4o entries
count = rc.invalidate_model("gpt-4o")
print(f"Removed {count} gpt-4o entries")

# gpt-4o-mini entry is untouched
print(rc.get(msgs, "gpt-4o-mini"))  # "Hola!"
```

### 10.2 Invalidate a user session

```python
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder,
    InvalidationEngine, ContextCache,
)

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
    invalidation_engine=InvalidationEngine(InMemoryBackend()),
)
ctx = ContextCache(manager)

ctx.set("user-123", 0, [{"role": "user", "content": "Hello"}])
ctx.set("user-123", 1, [{"role": "assistant", "content": "Hi there!"}])

ctx.invalidate_session("user-123")  # removes all turns for user-123
print(ctx.get("user-123", 0))  # None
```

### 10.3 Custom tags across frameworks

```python
from chengeta_ai import (
    CacheManager, InMemoryBackend, CacheKeyBuilder, InvalidationEngine,
)

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(namespace="multi"),
    invalidation_engine=InvalidationEngine(InMemoryBackend()),
)

# Tag entries with a deployment version
manager.set("k1", "v1", tags=["deploy:v1.0", "env:prod"])
manager.set("k2", "v2", tags=["deploy:v1.0", "env:prod"])
manager.set("k3", "v3", tags=["deploy:v2.0", "env:prod"])

# After deploying v2.0 — clear all v1.0 cache
count = manager.invalidate("deploy:v1.0")
print(f"Cleared {count} entries from v1.0 deploy")

# v2.0 entry is untouched
print(manager.get("k3"))  # "v3"
```

---

## 11. TTL Policies

### 11.1 Global TTL

```python
from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder, TTLPolicy

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
    ttl_policy=TTLPolicy(default_ttl=600),  # 10 minutes for everything
)
```

### 11.2 Per-layer TTL

```python
from chengeta_ai import TTLPolicy, CacheManager, InMemoryBackend, CacheKeyBuilder

policy = TTLPolicy(
    default_ttl=3600,
    per_type={
        "embed":     86_400,   # 24 h — embeddings rarely change
        "retrieval": 3_600,    # 1 h  — document corpus updates hourly
        "context":   1_800,    # 30 min — session context
        "response":  300,      # 5 min — LLM responses can go stale
    },
)
manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
    ttl_policy=policy,
)
```

### 11.3 Per-layer TTL from environment

```bash
export CHENGETA_TTL_EMBEDDING=86400
export CHENGETA_TTL_RETRIEVAL=3600
export CHENGETA_TTL_CONTEXT=1800
export CHENGETA_TTL_RESPONSE=300
```

```python
from chengeta_ai import CacheManager, ChengetaSettings

manager = CacheManager.from_settings(ChengetaSettings.from_env())
```

### 11.4 No TTL (cache forever)

```python
from chengeta_ai import TTLPolicy, CacheManager, InMemoryBackend, CacheKeyBuilder

manager = CacheManager(
    backend=InMemoryBackend(),
    key_builder=CacheKeyBuilder(),
    ttl_policy=TTLPolicy(default_ttl=None),  # None = no expiry
)
```

---

## 12. Multi-Framework Pipeline

A complete example that wires **LangChain** LLM caching, **LangGraph** state persistence,
**Agno** agent caching, and **A2A** inter-agent caching into a single shared `CacheManager`.

```python
"""
Pipeline:
  User query
    → LangChain (cached LLM call) → outline
    → LangGraph (stateful graph, checkpointed) → structured plan
    → Agno agent (cached) → detailed write-up
    → A2A reviewer (cached) → final review
"""
import asyncio
import numpy as np

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.globals import set_llm_cache
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from agno.agent import Agent as AgnoAgent
from agno.models.openai import OpenAIChat
from typing import Annotated, TypedDict

from chengeta_ai import (
    CacheManager, DiskBackend, CacheKeyBuilder,
    InvalidationEngine, InMemoryBackend,
    TTLPolicy, EmbeddingCache,
)
from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
from chengeta_ai.adapters.langgraph_adapter import LangGraphCacheAdapter
from chengeta_ai.adapters.agno_adapter import AgnoCacheAdapter
from chengeta_ai.adapters.a2a_adapter import A2ACacheAdapter

# ── Shared cache manager ───────────────────────────────────────────────────
manager = CacheManager(
    backend=DiskBackend(path="/var/cache/pipeline"),
    key_builder=CacheKeyBuilder(namespace="pipeline"),
    ttl_policy=TTLPolicy(
        default_ttl=3600,
        per_type={"embed": 86400, "response": 600},
    ),
    invalidation_engine=InvalidationEngine(InMemoryBackend()),
)

# ── 1. LangChain — cache all LLM calls globally ────────────────────────────
set_llm_cache(LangChainCacheAdapter(manager))
llm = ChatOpenAI(model="gpt-4o-mini")

# ── 2. LangGraph — stateful agent graph ───────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]
    plan: str

def outline_node(state: State) -> State:
    resp = llm.invoke([
        {"role": "system", "content": "Create a numbered outline (max 5 points)."},
        *state["messages"],
    ])
    return {"plan": resp.content}

builder = StateGraph(State)
builder.add_node("outline", outline_node)
builder.set_entry_point("outline")
builder.add_edge("outline", END)

checkpointer = LangGraphCacheAdapter(manager)
graph = builder.compile(checkpointer=checkpointer)

# ── 3. Agno — cached writer agent ─────────────────────────────────────────
writer_agent = AgnoAgent(
    model=OpenAIChat(id="gpt-4o-mini"),
    description="Expand an outline into prose.",
)
cached_writer = AgnoCacheAdapter(writer_agent, manager)

# ── 4. A2A — cached reviewer ───────────────────────────────────────────────
reviewer_adapter = A2ACacheAdapter(manager, agent_id="reviewer")

async def review_fn(payload: dict) -> dict:
    resp = llm.invoke([
        {"role": "system", "content": "Review and improve the text. Return the improved version."},
        {"role": "user",   "content": payload["text"]},
    ])
    return {"reviewed": resp.content}

# ── 5. Embeddings cache ────────────────────────────────────────────────────
embedder = OpenAIEmbeddings(model="text-embedding-3-small")
emb_cache = EmbeddingCache(manager)

# ── Pipeline ───────────────────────────────────────────────────────────────
async def run_pipeline(query: str) -> str:
    config = {"configurable": {"thread_id": f"pipeline-{hash(query)}"}}

    # Step 1: LangGraph outline (checkpointed)
    state = graph.invoke(
        {"messages": [("user", query)], "plan": ""},
        config=config,
    )
    outline = state["plan"]
    print("Outline:\n", outline)

    # Step 2: Agno writer (cached)
    write_result = await cached_writer.arun(
        f"Expand this outline into a short article:\n{outline}"
    )
    article = write_result.content
    print("\nDraft:\n", article[:300], "...")

    # Step 3: A2A reviewer (cached)
    reviewed = await reviewer_adapter.aprocess(review_fn, {"text": article})
    print("\nReviewed:\n", reviewed["reviewed"][:300], "...")

    # Step 4: Embed the final article (cached)
    vec = emb_cache.get_or_compute(
        text=reviewed["reviewed"],
        compute_fn=lambda t: np.array(embedder.embed_query(t), dtype=np.float32),
        model_id="text-embedding-3-small",
    )
    print(f"\nEmbedding shape: {vec.shape}")

    return reviewed["reviewed"]

if __name__ == "__main__":
    result = asyncio.run(run_pipeline("Write about the impact of caching on AI systems."))
    # Run again — every step served from cache
    result2 = asyncio.run(run_pipeline("Write about the impact of caching on AI systems."))
    assert result == result2
    print("\nAll steps cached correctly!")
```

---

## Appendix: Framework Compatibility Matrix

| Feature | LangChain | LangGraph | AutoGen 0.4+ | AutoGen 0.2.x | CrewAI | Agno | A2A |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Response cache | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Embedding cache | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| Retrieval cache | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| Context cache | ✅ | ✅ | — | — | — | ✅ | — |
| Semantic cache | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| State checkpoint | — | ✅ | — | — | — | — | — |
| Tag invalidation | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Async support | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| InMemory backend | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Disk backend | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Redis backend | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| FAISS backend | ✅ | — | ✅ | ✅ | — | ✅ | — |

## Appendix: Quick Install Reference

```bash
# Core only
pip install chengeta-ai

# Per-framework
pip install 'chengeta-ai[langchain]'         # LangChain
pip install 'chengeta-ai[langgraph]'         # LangGraph
pip install 'chengeta-ai[autogen]'           # AutoGen legacy (pyautogen)
pip install 'autogen-agentchat>=0.4'          # AutoGen new API (separate package)
pip install 'chengeta-ai[crewai]'            # CrewAI
pip install 'chengeta-ai[agno]'              # Agno
pip install 'a2a-sdk>=0.3' chengeta-ai       # A2A

# Backends
pip install 'chengeta-ai[redis]'             # Redis
pip install 'chengeta-ai[vector-faiss]'      # FAISS semantic cache
pip install 'chengeta-ai[vector-chroma]'     # ChromaDB semantic cache

# Everything
pip install 'chengeta-ai[all]'
```
