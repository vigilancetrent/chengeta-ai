from __future__ import annotations
from chengeta_ai import CacheKeyBuilder, CacheManager, InMemoryBackend, InvalidationEngine

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    manager = CacheManager(
        backend=InMemoryBackend(),
        key_builder=CacheKeyBuilder(namespace="cookbook-inv"),
        invalidation_engine=InvalidationEngine(InMemoryBackend()),
    )
    t0 = time.perf_counter()
    manager.set("k1", "v1", tags=["model:gemma3:4b"])
    manager.set("k2", "v2", tags=["model:gemma3:4b"])
    t1 = time.perf_counter()
    print(f"set 2 keys : {t1 - t0:.6f}s")

    t2 = time.perf_counter()
    count = manager.invalidate("model:gemma3:4b")
    t3 = time.perf_counter()
    print(f"invalidate : {t3 - t2:.6f}s  (evicted {count} keys)")


if __name__ == "__main__":
    main()
