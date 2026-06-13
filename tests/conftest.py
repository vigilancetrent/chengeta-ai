"""Shared test fixtures."""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from chengeta_ai.backends.memory_backend import InMemoryBackend
from chengeta_ai.backends.disk_backend import DiskBackend
from chengeta_ai.core.cache_manager import CacheManager
from chengeta_ai.core.key_builder import CacheKeyBuilder
from chengeta_ai.core.policies import TTLPolicy


@pytest.fixture(params=["memory", "disk"], ids=["memory", "disk"])
def backend(request: pytest.FixtureRequest, tmp_path: pytest.TempPathFactory):
    """Parametrised fixture covering InMemoryBackend and DiskBackend."""
    if request.param == "memory":
        b = InMemoryBackend()
        yield b
        b.close()
    else:
        b = DiskBackend(str(tmp_path / "cache"))
        yield b
        b.close()


@pytest.fixture
def key_builder() -> CacheKeyBuilder:
    return CacheKeyBuilder(namespace="test")


@pytest.fixture
def cache_manager(tmp_path) -> CacheManager:
    return CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="test"),
        ttl_policy=TTLPolicy(default_ttl=None),
    )


def mock_embed(text: str) -> np.ndarray:
    """Deterministic mock embedding: hash text to a normalised float32 vector."""
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)  # noqa: S324
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(1536).astype(np.float32)
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v
