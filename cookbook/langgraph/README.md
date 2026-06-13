# LangGraph + Chengeta + Ollama (Real-World Agent)

This example builds a **production-style incident triage workflow**:

1. classify incident severity
2. generate an action plan
3. persist thread state via LangGraph checkpointer
4. cache repeated LLM calls via Chengeta

Model used: `gemma3:4b` from local Ollama.

## Install

```bash
# Option A (local repo)
pip install -e .
pip install "chengeta-ai[langgraph]" langchain-ollama

# Option B (README-recommended GitHub install)
# pip install "chengeta-ai[langgraph] @ git+https://github.com/vigilancetrent/chengeta-ai.git"
# pip install langchain-ollama
```

## Run

```bash
python cookbook/langgraph/agent.py
```

## Integration Notes

- Replace in-memory backend with Redis/Disk for multi-instance services.
- Keep `thread_id` stable per user/session to resume conversations.
- Add tags (e.g., `service:payments`) for targeted invalidation.
