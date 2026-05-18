from __future__ import annotations

import json

import structlog

from kmg_shared.errors import IngestionError
from kmg_shared.ports.queue import JobQueue
from kmg_shared.repositories.job_repo import JobRepository
from kmg_worker.job_runner import WorkflowRunner

logger = structlog.get_logger()


class IngestionConsumer:
    def __init__(
        self,
        queue: JobQueue,
        job_repo: JobRepository,
        workflow_runner: WorkflowRunner,
    ) -> None:
        self._queue = queue
        self._job_repo = job_repo
        self._runner = workflow_runner

    async def run_forever(self) -> None:
        """Claim jobs from queue, run SimpleAgents workflows."""
        logger.info("consumer_started", queue="ingestion")
        async for message in self._queue.consume("ingestion"):
            job = await self._job_repo.get_by_id_or_raise(message.job_id)
            logger.info("job_claimed", job_id=message.job_id, source_id=str(job.source_id))
            try:
                await self._job_repo.update_status(job.id, "processing")
                await self._runner.run_ingestion(job)
                await self._job_repo.update_status(job.id, "completed", progress=1.0)
                await self._queue.ack("ingestion", message.job_id)
            except IngestionError as e:
                if e.retryable:
                    logger.warning("ingestion_retryable", job_id=message.job_id, error=str(e))
                    await self._job_repo.update_status(job.id, "failed", error=str(e))
                    await self._queue.nack("ingestion", message.job_id)
                else:
                    logger.error("ingestion_permanent_failure", job_id=message.job_id, error=str(e))
                    await self._job_repo.update_status(job.id, "failed", error=str(e))
                    await self._queue.ack("ingestion", message.job_id)
                    await self._push_to_dlq(message.job_id, str(e))
            except Exception as e:
                logger.error("ingestion_unexpected_failure", job_id=message.job_id, error=str(e))
                await self._job_repo.update_status(job.id, "failed", error=str(e))
                await self._queue.ack("ingestion", message.job_id)
                await self._push_to_dlq(message.job_id, str(e))

    async def _push_to_dlq(self, job_id: str, error: str) -> None:
        """Push failed job details to a Redis DLQ list for later inspection."""
        try:
            payload = json.dumps({"job_id": job_id, "error": error})
            await self._queue.push_to_dlq("kmg:dlq:ingestion", payload)
        except Exception:
            logger.error("dlq_push_failed", job_id=job_id, exc_info=True)
