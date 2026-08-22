"""Response caching for slow-changing external/reference data.

Good candidates (and default TTLs):

* weather forecast          — 30 minutes
* market metadata (mandis)  — 1 hour
* crop / disease / pest reference info — 1 hour

Rapidly changing or user-specific data must NOT be cached here.

Two backends share one interface:

* ``MemoryCache``  — process-local TTL store (default; zero infrastructure)
* ``RedisCache``   — used automatically when ``REDIS_URL`` is set and the
  optional ``redis`` package is installed (see docker-compose)

Cache keys always include the relevant query parameters so two different
queries can never collide.
"""

import json
import logging
import time
from typing import Any, Protocol

from app.core.config import get_settings

logger = logging.getLogger("agrisense.cache")

WEATHER_TTL = 30 * 60
MARKET_METADATA_TTL = 60 * 60
REFERENCE_INFO_TTL = 60 * 60


class CacheBackend(Protocol):
    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, ttl: int) -> None: ...
    async def close(self) -> None: ...


class MemoryCache:
    """Process-local TTL cache. Entries are JSON-serializable values."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    async def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at < time.monotonic():
            self._store.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: Any, ttl: int) -> None:
        self._store[key] = (time.monotonic() + ttl, value)

    async def close(self) -> None:
        self._store.clear()


class RedisCache:
    """Redis-backed cache. Keys are namespaced ``agrisense:<key>``."""

    def __init__(self, url: str) -> None:
        import redis.asyncio as aioredis  # optional dependency

        self._redis = aioredis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> Any | None:
        raw = await self._redis.get(f"agrisense:{key}")
        return json.loads(raw) if raw is not None else None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        await self._redis.set(f"agrisense:{key}", json.dumps(value), ex=ttl)

    async def close(self) -> None:
        await self._redis.aclose()


_cache: CacheBackend | None = None


async def get_cache() -> CacheBackend:
    global _cache  # noqa: PLW0603
    if _cache is None:
        settings = get_settings()
        if settings.redis_url:
            try:
                _cache = RedisCache(settings.redis_url)
                logger.info("cache backend=redis")
            except ImportError:
                logger.warning("redis package not installed; using memory cache")
                _cache = MemoryCache()
        else:
            _cache = MemoryCache()
    return _cache


async def close_cache() -> None:
    global _cache  # noqa: PLW0603
    if _cache is not None:
        await _cache.close()
        _cache = None


def cache_key(prefix: str, **params: Any) -> str:
    """Build a deterministic cache key that includes all query parameters."""
    parts = [prefix] + [f"{k}={params[k]}" for k in sorted(params)]
    return ":".join(parts)
