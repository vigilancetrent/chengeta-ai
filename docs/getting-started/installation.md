# Installation

## Requirements

- **Python** >= 3.12
- **Core dependencies**: `diskcache`, `numpy` (installed automatically)

---

## Install from GitHub (available now)

=== "pip"

    ```bash
    pip install git+https://github.com/vigilancetrent/chengeta-ai.git
    ```

=== "uv"

    ```bash
    uv add git+https://github.com/vigilancetrent/chengeta-ai.git
    ```

=== "With extras"

    ```bash
    pip install "chengeta-ai[langchain,redis] @ git+https://github.com/vigilancetrent/chengeta-ai.git"
    ```

---

## Install from PyPI (coming soon)

=== "pip"

    ```bash
    # Core (in-memory + disk backends)
    pip install chengeta-ai

    # With framework adapters
    pip install 'chengeta-ai[langchain]'
    pip install 'chengeta-ai[langgraph]'
    pip install 'chengeta-ai[crewai]'
    pip install 'chengeta-ai[agno]'

    # With storage backends
    pip install 'chengeta-ai[redis]'
    pip install 'chengeta-ai[vector-faiss]'
    pip install 'chengeta-ai[vector-chroma]'

    # Everything
    pip install 'chengeta-ai[all]'
    ```

=== "uv"

    ```bash
    uv add chengeta-ai
    uv add 'chengeta-ai[langchain,redis]'
    uv add 'chengeta-ai[all]'
    ```

=== "conda"

    ```bash
    conda install -c conda-forge chengeta-ai
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
# 0.1.0
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

!!! tip "AutoGen 0.4+"
    For the new AutoGen API, install `autogen-agentchat>=0.4` separately:
    ```bash
    pip install 'autogen-agentchat>=0.4' chengeta-ai
    ```
