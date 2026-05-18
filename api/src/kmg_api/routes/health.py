"""Health check endpoints."""
from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from kmg_shared.db.session import get_session_factory
from kmg_shared.infra.registry import get_cache

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "service": "kmg-api", "version": "0.1.0"}


@router.get("/ready")
async def readiness_check() -> dict:
    components: dict[str, str] = {}

    # Check database
    try:
        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        components["database"] = "ok"
    except Exception as e:
        components["database"] = f"error: {e}"

    # Check Redis/cache
    try:
        cache = get_cache()
        await cache.ping()
        components["redis"] = "ok"
    except Exception as e:
        components["redis"] = f"error: {e}"

    all_ok = all(v == "ok" for v in components.values())
    return {
        "status": "ready" if all_ok else "degraded",
        "components": components,
    }
