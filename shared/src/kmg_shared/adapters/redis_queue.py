from __future__ import annotations

import json
from collections.abc import AsyncIterator

import redis.asyncio as redis

from kmg_shared.ports.queue import JobMessage
from kmg_shared.resilience import retry_transient


class RedisJobQueue:
    """JobQueue implementation backed by Redis lists."""

    def __init__(self, url: str) -> None:
        self._redis = redis.from_url(url, decode_responses=True)

    def _processing_key(self, queue_name: str) -> str:
        return f"{queue_name}:processing"

    @retry_transient
    async def enqueue(self, queue_name: str, job_id: str, payload: dict | None = None) -> None:
        message = json.dumps({"job_id": job_id, "payload": payload or {}})
        await self._redis.lpush(queue_name, message)

    async def consume(self, queue_name: str) -> AsyncIterator[JobMessage]:
        while True:
            result = await self._redis.brpop(queue_name, timeout=5)
            if result is None:
                continue
            _, raw = result
            data = json.loads(raw)
            await self._redis.sadd(self._processing_key(queue_name), data["job_id"])
            yield JobMessage(job_id=data["job_id"], payload=data["payload"])

    async def ack(self, queue_name: str, job_id: str) -> None:
        await self._redis.srem(self._processing_key(queue_name), job_id)

    async def nack(self, queue_name: str, job_id: str) -> None:
        await self._redis.srem(self._processing_key(queue_name), job_id)
        message = json.dumps({"job_id": job_id, "payload": {}})
        await self._redis.lpush(queue_name, message)

    async def push_to_dlq(self, dlq_key: str, payload: str) -> None:
        await self._redis.lpush(dlq_key, payload)
