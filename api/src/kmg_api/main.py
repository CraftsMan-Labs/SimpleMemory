from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from kmg_api.config import api_settings
from kmg_api.middleware.correlation import CorrelationIdMiddleware
from kmg_api.middleware.logging import RequestLoggingMiddleware
from kmg_api.middleware.metrics import MetricsMiddleware
from kmg_api.routes import include_routers
from kmg_shared.config import settings as shared_settings
from kmg_shared.logging import configure_logging
from kmg_shared.tracing import configure_tracing
from kmg_shared.errors import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
)


def create_app() -> FastAPI:
    configure_logging()
    configure_tracing("kmg-api", shared_settings.otlp_endpoint or None)

    app = FastAPI(
        title="Knowledge Memory Graph API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(MetricsMiddleware)

    include_routers(app)
    _register_error_handlers(app)

    return app


def _register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc), "entity": exc.entity})

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(request: Request, exc: PermissionDeniedError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc), "field": exc.field})

    @app.exception_handler(ConflictError)
    async def conflict_error_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc), "entity": exc.entity})

    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(request: Request, exc: RateLimitError) -> JSONResponse:
        headers = {}
        if exc.retry_after is not None:
            headers["Retry-After"] = str(exc.retry_after)
        return JSONResponse(status_code=429, content={"detail": str(exc)}, headers=headers)


app = create_app()
