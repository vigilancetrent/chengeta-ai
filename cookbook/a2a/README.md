# A2A + Chengeta + Ollama (Real-World Multi-Agent Pipeline)

This example builds a practical **planner → executor → reviewer** pipeline:

- Planner creates implementation steps
- Executor turns plan into concrete actions
- Reviewer checks quality and rollout safety

Each stage is cached through `A2ACacheAdapter` so repeated requests skip
re-running expensive LLM calls.

Model used: `gemma3:4b` from local Ollama via `langchain-ollama`.

## Install

```bash
# Option A (local repo)
uv pip install -e .
uv pip install langchain-ollama

# Option B (README-recommended GitHub install)
# uv pip install "chengeta-ai @ git+https://github.com/vigilancetrent/chengeta-ai.git"
# uv pip install langchain-ollama
```

## Run

```bash
uv run python -m cookbook.a2a.agent
```

## Integration Notes

- Map each adapter to a real service/team role in your architecture.
- Add TTL and tags (`project:x`, `release:y`) for governance.
- Replace in-memory backend with Redis for distributed worker pools.
