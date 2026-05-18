from __future__ import annotations

from fastapi import FastAPI

from kmg_api.routes.canvas import router as canvas_router
from kmg_api.routes.graph import router as graph_router
from kmg_api.routes.health import router as health_router
from kmg_api.routes.search import router as search_router
from kmg_api.routes.sources import router as sources_router
from kmg_api.routes.wiki import router as wiki_router
from kmg_api.routes.workspaces import router as workspaces_router


def include_routers(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(workspaces_router)
    app.include_router(sources_router)
    app.include_router(wiki_router)
    app.include_router(graph_router)
    app.include_router(search_router)
    app.include_router(canvas_router)
