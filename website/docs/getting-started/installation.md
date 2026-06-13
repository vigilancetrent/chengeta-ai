---
title: "Installation"
---

# Installation

## Requirements

- **Python** >= 3.12
- **Core dependencies**: `diskcache`, `numpy` (installed automatically)

---

## Install from PyPI

```bash
# Core (in-memory + disk backends)
pip install chengeta-ai

# With framework adapters
pip install 'chengeta-ai[langchain]'
pip install 'chengeta-ai[langgraph]'
pip install 'chengeta-ai[autogen]'
pip install 'chengeta-ai[crewai]'
pip install 'chengeta-ai[agno]'

# With storage backends
pip install 'chengeta-ai[redis]'
pip install 'chengeta-ai[vector-faiss]'
pip install 'chengeta-ai[vector-chroma]'

# Everything
pip install 'chengeta-ai[all]'
```

### uv

```bash
uv add chengeta-ai
uv add 'chengeta-ai[langchain,redis]'
uv add 'chengeta-ai[all]'
```

---

## From Source

```bash
git clone https://github.com/vigilancetrent/chengeta-ai.git
cd chengeta-ai
uv sync --dev
uv run pytest  # verify install
```

---

## Verify Installation

```bash
python -c "import chengeta_ai; print(chengeta_ai.__version__)"
# 0.2.0
```

---

## Optional Dependencies

| Extra | Package | What it enables |
|---|---|---|
| `redis` | `redis>=5.0` | Redis-backed distributed cache |
| `vector-faiss` | `faiss-cpu>=1.7` | FAISS vector similarity search |
| `vector-chroma` | `chromadb>=0.4` | ChromaDB persistent vector store |
| `langchain` | `langchain-core>=0.2` | LangChain `BaseCache` adapter |
| `langgraph` | `langgraph>=0.1` | LangGraph checkpoint adapter |
| `autogen` | `pyautogen>=0.2` | AutoGen 0.2.x adapter |
| `crewai` | `crewai>=0.28` | CrewAI kickoff adapter |
| `agno` | `agno>=0.1` | Agno agent adapter |
| `openai` | `openai>=1.0` | OpenAI SDK adapter |
| `anthropic` | `anthropic>=0.25` | Anthropic SDK adapter |

> **AutoGen 0.4+**: install `autogen-agentchat>=0.4` separately — it ships as its own package.

---

## Docker

```bash
docker build -t chengeta-ai .
docker run --rm chengeta-ai
```
