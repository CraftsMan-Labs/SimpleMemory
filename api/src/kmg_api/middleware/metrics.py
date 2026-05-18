"""Prometheus metrics middleware for FastAPI."""
from __future__ import annotations

import time

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from kmg_shared.metrics import (
    ERROR_COUNT,
    REQUEST_COUNT,
    REQUEST_LATENCY,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        path = request.url.path

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - start
            REQUEST_LATENCY.labels(
                method=method, endpoint=path, status="500"
            ).observe(duration)
            REQUEST_COUNT.labels(
                method=method, endpoint=path, status="500"
            ).inc()
            ERROR_COUNT.labels(
                method=method,
                endpoint=path,
                error_type=type(exc).__name__,
            ).inc()
            raise

        duration = time.perf_counter() - start
        status = str(response.status_code)
        REQUEST_LATENCY.labels(
            method=method, endpoint=path, status=status
        ).observe(duration)
        REQUEST_COUNT.labels(
            method=method, endpoint=path, status=status
        ).inc()
        if response.status_code >= 400:
            ERROR_COUNT.labels(
                method=method,
                endpoint=path,
                error_type=f"http_{status}",
            ).inc()
        return response
