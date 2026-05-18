from __future__ import annotations

import redis.asyncio as redis


class RedisCacheAdapter:
    """Cache implementation backed by Redis."""

    def __init__(self, url: str) -> None:
        self._redis = redis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        value = await self._redis.get(key)
        return value

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        await self._redis.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._redis.exists(key))

    async def ping(self) -> bool:
        return await self._redis.ping()
