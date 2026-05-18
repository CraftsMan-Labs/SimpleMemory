"""Verify port protocols are importable and structurally correct."""
from __future__ import annotations

from kmg_shared.ports import (
    Cache, EmbeddingProvider, JobMessage, JobQueue,
    ObjectStorage, ScoredResult, VectorDB, VectorRecord,
)


def test_protocols_importable():
    """All protocol classes should be importable."""
    assert ObjectStorage is not None
    assert VectorDB is not None
    assert JobQueue is not None
    assert EmbeddingProvider is not None
    assert Cache is not None


def test_dataclasses_importable():
    """Supporting dataclasses should be importable."""
    assert VectorRecord is not None
    assert ScoredResult is not None
    assert JobMessage is not None


def test_vector_record_creation():
    record = VectorRecord(id="test-1", vector=[0.1, 0.2, 0.3], payload={"key": "value"})
    assert record.id == "test-1"
    assert len(record.vector) == 3


def test_scored_result_creation():
    result = ScoredResult(id="test-1", score=0.95, payload={"title": "Test"})
    assert result.score == 0.95


def test_job_message_creation():
    msg = JobMessage(job_id="job-123", payload={"source_id": "src-1"})
    assert msg.job_id == "job-123"
