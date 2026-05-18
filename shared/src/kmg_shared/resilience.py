"""Reusable retry decorators for external service calls."""
from __future__ import annotations

import structlog
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = structlog.get_logger()

retry_transient = retry(
    retry=retry_if_exception_type((OSError, TimeoutError, ConnectionError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=60),
    before_sleep=before_sleep_log(logger, "WARNING"),  # type: ignore[arg-type]
    reraise=True,
)
"""Decorator for external service calls (embedding, Qdrant, S3, Redis).

Retries on transient network/timeout errors with exponential backoff + jitter,
up to 3 attempts with a 60s max delay between attempts.
"""
