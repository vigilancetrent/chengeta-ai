# CrewAI

Cache CrewAI crew kickoff results, invalidate stale entries after re-training,
and combine with retrieval caching for knowledge-base tools.

```bash
pip install 'chengeta-ai[crewai]'
```

---

## 5.1 Basic crew with cached kickoff

Wrap a `Crew` so that identical inputs return the cached result instantly.

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

---

## 5.2 Async crew kickoff

Use the async interface for non-blocking crew execution with disk-backed persistence.

```python
import asyncio
from crewai import Agent, Task, Crew
from chengeta_ai import CacheManager, DiskBackend, CacheKeyBuilder
from chengeta_ai.adapters.crewai_adapter import CrewAICacheAdapter

manager = CacheManager(
    backend=DiskBackend(directory="/var/cache/crew"),
    key_builder=CacheKeyBuilder(namespace="crew"),
)

# ... (define agents, tasks, crew as above)

async def main():
    cached_crew = CrewAICacheAdapter(crew, manager)
    result = await cached_crew.kickoff_async(inputs={"topic": "LLM fine-tuning"})
    print(result)

asyncio.run(main())
```

---

## 5.3 Cache invalidation after crew re-training

Tag cached results and invalidate them in bulk when you retrain or update agents.

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

---

## 5.4 Crew + retrieval cache for knowledge base

Combine crew caching with a `RetrievalCache` so repeated knowledge-base lookups are instant.

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
