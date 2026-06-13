# Semantic Cache

Run:

```bash
uv run python -m cookbook.semantic_cache.agent
```

Uses Ollama embeddings (`nomic-embed-text`) and FAISS backend.

Prerequisites:

```bash
ollama pull nomic-embed-text
uv pip install faiss-cpu
```
