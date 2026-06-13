# Agno + Chengeta + Ollama (Real-World Agent)

This example creates a **policy analyst agent** for engineering teams.

It generates a deployment-risk memo from release notes and uses Chengeta
to avoid recomputing identical analysis.

Model used: `gemma3:4b` through Ollama OpenAI-compatible endpoint.

## Install

```bash
# Option A (local repo)
pip install -e .
pip install "chengeta-ai[agno]"

# Option B (README-recommended GitHub install)
# pip install "chengeta-ai[agno] @ git+https://github.com/vigilancetrent/chengeta-ai.git"
```

## Run

```bash
python cookbook/agno/agent.py
```

## Integration Notes

- Use `DiskBackend`/`RedisBackend` when running multiple workers.
- Keep model + prompt version in tags to invalidate old memo logic.
- Expose `generate_memo()` via your API endpoint for product teams.
