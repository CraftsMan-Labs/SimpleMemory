from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol


@dataclass
class JobMessage:
    job_id: str
    payload: dict


class JobQueue(Protocol):
    """Abstract job queue -- swap Redis/SQS/RabbitMQ."""

    async def enqueue(self, queue_name: str, job_id: str, payload: dict | None = None) -> None: ...
    def consume(self, queue_name: str) -> AsyncIterator[JobMessage]: ...
    async def ack(self, queue_name: str, job_id: str) -> None: ...
    async def nack(self, queue_name: str, job_id: str) -> None: ...
    async def push_to_dlq(self, dlq_key: str, payload: str) -> None: ...
