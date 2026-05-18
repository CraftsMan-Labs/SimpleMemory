"""Test the error hierarchy."""
from __future__ import annotations

import uuid

from kmg_shared.errors import (
    AuthenticationError,
    ConflictError,
    IngestionError,
    KmgError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    SourceUploadNotFoundError,
    ValidationError,
)


def test_all_errors_inherit_from_kmg_error():
    for cls in [NotFoundError, PermissionDeniedError, ValidationError,
                ConflictError, IngestionError, SourceUploadNotFoundError,
                AuthenticationError, RateLimitError]:
        assert issubclass(cls, KmgError)


def test_not_found_error():
    err = NotFoundError("WikiPage", "abc-123")
    assert "WikiPage" in str(err)
    assert "abc-123" in str(err)
    assert err.entity == "WikiPage"


def test_ingestion_error_retryable():
    err = IngestionError("timeout", retryable=True)
    assert err.retryable is True

    err2 = IngestionError("corrupt file", retryable=False)
    assert err2.retryable is False


def test_source_upload_not_found():
    sid = uuid.uuid4()
    vid = uuid.uuid4()
    err = SourceUploadNotFoundError(sid, vid)
    assert err.source_id == sid
    assert err.version_id == vid
    assert "presigned" in str(err).lower()


def test_rate_limit_retry_after():
    err = RateLimitError("slow down", retry_after=60)
    assert err.retry_after == 60


def test_validation_error_field():
    err = ValidationError("bad input", field="title")
    assert err.field == "title"
