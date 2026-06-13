# Migration Guide → Chengeta AI

This project was previously published under a different name. **Chengeta AI** is the same
multi-layer memory engine with a new identity, a cleaner public surface, and a brand built around
the chiShona verb *ku-chengeta* — *to store, preserve, and keep safe.*

If you are upgrading from the predecessor package, this guide covers every breaking rename. The
public **behaviour** of every class and method is unchanged — only names changed.

> **TL;DR:** `omnicache` → `chengeta` everywhere (package, import, env vars, CLI, namespace).

---

## 1. Package & install

| Before | After |
|--------|-------|
| `pip install omnicache-ai` | `pip install chengeta-ai` |
| `pip install 'omnicache-ai[redis]'` | `pip install 'chengeta-ai[redis]'` |
| `pip install 'omnicache-ai[all]'` | `pip install 'chengeta-ai[all]'` |

Uninstall the old package to avoid two copies on the path:

```bash
pip uninstall omnicache-ai
pip install chengeta-ai
```

## 2. Imports

```diff
- from omnicache_ai import CacheManager, InMemoryBackend, CacheKeyBuilder
+ from chengeta_ai import CacheManager, InMemoryBackend, CacheKeyBuilder

- from omnicache_ai.adapters.langchain_adapter import LangChainCacheAdapter
+ from chengeta_ai.adapters.langchain_adapter import LangChainCacheAdapter
```

The import root is the only thing that moved — every class, method, and signature is identical.

## 3. Renamed public symbols

| Before | After |
|--------|-------|
| `OmnicacheSettings` | `ChengetaSettings` |
| `OmnicacheEntry` | `ChengetaEntry` |

```diff
- from omnicache_ai import CacheManager, OmnicacheSettings
- manager = CacheManager.from_settings(OmnicacheSettings.from_env())
+ from chengeta_ai import CacheManager, ChengetaSettings
+ manager = CacheManager.from_settings(ChengetaSettings.from_env())
```

## 4. Environment variables

The `OMNICACHE_` prefix is now `CHENGETA_`. This is a **hard rename** — legacy variables are not
read. Update your `.env`, deployment manifests, and secrets.

| Before | After |
|--------|-------|
| `OMNICACHE_BACKEND` | `CHENGETA_BACKEND` |
| `OMNICACHE_REDIS_URL` | `CHENGETA_REDIS_URL` |
| `OMNICACHE_DISK_PATH` | `CHENGETA_DISK_PATH` |
| `OMNICACHE_DEFAULT_TTL` | `CHENGETA_DEFAULT_TTL` |
| `OMNICACHE_NAMESPACE` | `CHENGETA_NAMESPACE` |
| `OMNICACHE_SEMANTIC_THRESHOLD` | `CHENGETA_SEMANTIC_THRESHOLD` |
| `OMNICACHE_VECTOR_BACKEND` | `CHENGETA_VECTOR_BACKEND` |
| `OMNICACHE_EMBEDDING_DIM` | `CHENGETA_EMBEDDING_DIM` |
| `OMNICACHE_MAX_MEMORY_ENTRIES` | `CHENGETA_MAX_MEMORY_ENTRIES` |
| `OMNICACHE_KEY_HASH_ALGO` | `CHENGETA_KEY_HASH_ALGO` |
| `OMNICACHE_TTL_EMBEDDING` | `CHENGETA_TTL_EMBEDDING` |
| `OMNICACHE_TTL_RETRIEVAL` | `CHENGETA_TTL_RETRIEVAL` |
| `OMNICACHE_TTL_CONTEXT` | `CHENGETA_TTL_CONTEXT` |
| `OMNICACHE_TTL_RESPONSE` | `CHENGETA_TTL_RESPONSE` |

## 5. Default key namespace

The default namespace changed from `omnicache` to `chengeta`. Cache **keys are namespaced**, so a
fresh deploy starts with a cold cache under the new prefix. This is safe (entries simply re-populate)
but if you must preserve an existing populated store, pin the old namespace explicitly:

```python
from chengeta_ai import CacheKeyBuilder
key_builder = CacheKeyBuilder(namespace="omnicache")  # keep reading legacy keys
```

or set `CHENGETA_NAMESPACE=omnicache`.

## 6. CLI

| Before | After |
|--------|-------|
| `omnicache stats` | `chengeta stats` |
| `omnicache flush` | `chengeta flush` |
| `omnicache inspect KEY` | `chengeta inspect KEY` |

New in Chengeta AI: `chengeta version` and `chengeta info`.

## 7. Automated migration

Most codebases can be migrated with a single pass. From the root of your project:

```bash
# Python sources, configs, and docs — review the diff before committing.
grep -rIl --null -e omnicache -e OMNICACHE -e Omnicache -e OmniCache . \
  | xargs -0 sed -i \
      -e 's/omnicache_ai/chengeta_ai/g' \
      -e 's/omnicache-ai/chengeta-ai/g' \
      -e 's/OMNICACHE_/CHENGETA_/g' \
      -e 's/OmnicacheSettings/ChengetaSettings/g' \
      -e 's/OmnicacheEntry/ChengetaEntry/g' \
      -e 's/omnicache/chengeta/g' \
      -e 's/OmniCache/Chengeta/g' \
      -e 's/Omnicache/Chengeta/g'
```

Then reinstall and run your tests:

```bash
pip uninstall -y omnicache-ai && pip install chengeta-ai
pytest
```

---

If something is missing from this guide, please
[open an issue](https://github.com/vigilancetrent/chengeta-ai/issues).
