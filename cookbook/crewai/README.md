# CrewAI + Chengeta + Ollama (Real-World Crew)

This example implements a **release planning crew** with two roles:

- Reliability Engineer: identifies operational risk
- Release Manager: builds execution checklist

The complete crew output is cached with `CrewAICacheAdapter` so repeated
inputs skip expensive multi-agent re-runs.

Model used: `gemma3:4b` from local Ollama.

## Install

```bash
# Option A (local repo)
pip install -e .
pip install "chengeta-ai[crewai]"

# Option B (README-recommended GitHub install)
# pip install "chengeta-ai[crewai] @ git+https://github.com/vigilancetrent/chengeta-ai.git"
```

## Run

```bash
python cookbook/crewai/agent.py
```

## Integration Notes

- For production, move from `InMemoryBackend` to `RedisBackend`.
- Add tags (release version, service name) for controlled invalidation.
- Invoke this crew from CI/CD approval gates before deployment.
