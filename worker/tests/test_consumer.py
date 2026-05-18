"""Test IngestionConsumer with mocked dependencies."""
from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kmg_shared.errors import IngestionError
from kmg_shared.ports.queue import JobMessage
from kmg_worker.consumer import IngestionConsumer


@pytest.fixture
def queue():
    return AsyncMock()


@pytest.fixture
def job_repo():
    return AsyncMock()


@pytest.fixture
def workflow_runner():
    return AsyncMock()


@pytest.fixture
def consumer(queue, job_repo, workflow_runner):
    return IngestionConsumer(
        queue=queue,
        job_repo=job_repo,
        workflow_runner=workflow_runner,
    )


def _make_job(job_id=None, source_id=None):
    job = MagicMock()
    job.id = job_id or uuid.uuid4()
    job.source_id = source_id or uuid.uuid4()
    job.source_version_id = uuid.uuid4()
    job.tenant_id = uuid.uuid4()
    job.workspace_id = uuid.uuid4()
    job.pipeline_id = "default_pdf_pipeline"
    return job


def _make_message(job_id=None):
    jid = str(job_id or uuid.uuid4())
    return JobMessage(job_id=jid, payload={"source_id": str(uuid.uuid4())})


class TestSuccessfulJob:
    @pytest.mark.asyncio
    async def test_status_transitions_pending_to_completed(
        self, consumer, queue, job_repo, workflow_runner
    ):
        job_id = uuid.uuid4()
        message = _make_message(job_id)
        job = _make_job(job_id)

        async def _single_message(queue_name):
            yield message

        queue.consume = _single_message
        job_repo.get_by_id_or_raise.return_value = job

        # run_forever runs indefinitely; we break after one iteration via consume
        await consumer.run_forever()

        job_repo.update_status.assert_any_await(job.id, "processing")
        job_repo.update_status.assert_any_await(job.id, "completed", progress=1.0)
        workflow_runner.run_ingestion.assert_awaited_once_with(job)
        queue.ack.assert_awaited_once_with("ingestion", message.job_id)


class TestRetryableError:
    @pytest.mark.asyncio
    async def test_nacks_on_retryable_error(
        self, consumer, queue, job_repo, workflow_runner
    ):
        job_id = uuid.uuid4()
        message = _make_message(job_id)
        job = _make_job(job_id)

        async def _single_message(queue_name):
            yield message

        queue.consume = _single_message
        job_repo.get_by_id_or_raise.return_value = job
        workflow_runner.run_ingestion.side_effect = IngestionError("timeout", retryable=True)

        await consumer.run_forever()

        job_repo.update_status.assert_any_await(job.id, "processing")
        job_repo.update_status.assert_any_await(job.id, "failed", error="timeout")
        queue.nack.assert_awaited_once_with("ingestion", message.job_id)
        queue.ack.assert_not_awaited()


class TestPermanentError:
    @pytest.mark.asyncio
    async def test_acks_and_pushes_to_dlq(
        self, consumer, queue, job_repo, workflow_runner
    ):
        job_id = uuid.uuid4()
        message = _make_message(job_id)
        job = _make_job(job_id)

        async def _single_message(queue_name):
            yield message

        queue.consume = _single_message
        job_repo.get_by_id_or_raise.return_value = job
        workflow_runner.run_ingestion.side_effect = IngestionError("corrupt file", retryable=False)

        await consumer.run_forever()

        job_repo.update_status.assert_any_await(job.id, "failed", error="corrupt file")
        queue.ack.assert_awaited_once_with("ingestion", message.job_id)
        queue.nack.assert_not_awaited()
        queue.push_to_dlq.assert_awaited_once()
        dlq_payload = json.loads(queue.push_to_dlq.call_args[0][1])
        assert dlq_payload["job_id"] == message.job_id
        assert dlq_payload["error"] == "corrupt file"
