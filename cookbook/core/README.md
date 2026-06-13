# Core Setup + Layers (Ollama-Friendly)

Practical baseline setup for `chengeta-ai` before plugging into frameworks.

## Run

```bash
uv run python -m cookbook.core.agent
```

This demonstrates:

- `CacheManager` + `InMemoryBackend`
- `ResponseCache`
- `EmbeddingCache` with Ollama embeddings (`gemma3:4b` used via prompt flow)
