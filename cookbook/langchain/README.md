# LangChain + Chengeta + Ollama (Real-World Chain)

This example creates a **customer support answer assistant**:

- takes ticket + internal policy snippets
- drafts a concise support reply
- caches repeated prompts using `LangChainCacheAdapter`

Model used: `gemma3:4b` from local Ollama.

## Install

```bash
# Option A (local repo)
uv pip install -e .
uv pip install "chengeta-ai[langchain]" langchain-ollama

# Option B (README-recommended GitHub install)
# uv pip install "chengeta-ai[langchain] @ git+https://github.com/vigilancetrent/chengeta-ai.git"
# uv pip install langchain-ollama
```

## Run

```bash
uv run python -m cookbook.langchain.agent
```

## Integration Notes

- Use `RedisBackend` for shared cache across API replicas.
- Add tags (team, product area, prompt version) for controlled invalidation.
- Keep policy snippets versioned so stale answers are easy to invalidate.
