from __future__ import annotations

import uuid
from typing import Any

from kmg_shared.db.models.canvas import (
    WikiCanvas,
    WikiCanvasEdge,
    WikiCanvasItem,
)
from kmg_shared.errors import NotFoundError
from kmg_shared.repositories.canvas_repo import CanvasRepository


class CanvasService:
    def __init__(self, canvas_repo: CanvasRepository) -> None:
        self._canvas_repo = canvas_repo

    async def create_canvas(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        *,
        title: str,
        layout: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WikiCanvas:
        return await self._canvas_repo.create_canvas(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            title=title,
            layout=layout,
            metadata=metadata,
        )

    async def get_canvas(
        self, tenant_id: uuid.UUID, canvas_id: uuid.UUID
    ) -> tuple[WikiCanvas, list[WikiCanvasItem], list[WikiCanvasEdge]]:
        canvas, items, edges = await self._canvas_repo.get_with_items(
            canvas_id
        )
        if canvas.tenant_id != tenant_id:
            raise NotFoundError("Canvas", canvas_id)
        return canvas, items, edges

    async def list_canvases(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[WikiCanvas], int]:
        canvases = await self._canvas_repo.list_by_workspace(
            tenant_id, workspace_id, limit=limit, offset=offset
        )
        total = await self._canvas_repo.count_by_workspace(
            tenant_id, workspace_id
        )
        return canvases, total

    async def update_canvas(
        self,
        tenant_id: uuid.UUID,
        canvas_id: uuid.UUID,
        *,
        title: str | None = None,
        layout: dict[str, Any] | None = None,
    ) -> WikiCanvas:
        canvas = await self._canvas_repo.get_by_id(canvas_id)
        if canvas is None or canvas.tenant_id != tenant_id:
            raise NotFoundError("Canvas", canvas_id)

        if layout is not None:
            canvas = await self._canvas_repo.update_layout(canvas_id, layout)

        if title is not None:
            canvas.title = title  # type: ignore[assignment]

        return canvas

    async def delete_canvas(
        self, tenant_id: uuid.UUID, canvas_id: uuid.UUID
    ) -> None:
        canvas = await self._canvas_repo.get_by_id(canvas_id)
        if canvas is None or canvas.tenant_id != tenant_id:
            raise NotFoundError("Canvas", canvas_id)
        await self._canvas_repo._session.delete(canvas)
        await self._canvas_repo._session.flush()

    async def add_items(
        self,
        tenant_id: uuid.UUID,
        canvas_id: uuid.UUID,
        items: list[dict[str, Any]],
    ) -> list[WikiCanvasItem]:
        canvas = await self._canvas_repo.get_by_id(canvas_id)
        if canvas is None or canvas.tenant_id != tenant_id:
            raise NotFoundError("Canvas", canvas_id)
        return await self._canvas_repo.add_items_batch(canvas_id, items)

    async def add_edges(
        self,
        tenant_id: uuid.UUID,
        canvas_id: uuid.UUID,
        edges: list[dict[str, Any]],
    ) -> list[WikiCanvasEdge]:
        canvas = await self._canvas_repo.get_by_id(canvas_id)
        if canvas is None or canvas.tenant_id != tenant_id:
            raise NotFoundError("Canvas", canvas_id)
        return await self._canvas_repo.add_edges_batch(canvas_id, edges)

    async def ai_organize(
        self, tenant_id: uuid.UUID, canvas_id: uuid.UUID
    ) -> dict[str, Any]:
        canvas, items, edges = await self.get_canvas(tenant_id, canvas_id)
        # Basic auto-layout: grid arrangement
        items_moved = 0
        for i, item in enumerate(items):
            col = i % 4
            row = i // 4
            item.x = col * 250.0  # type: ignore[assignment]
            item.y = row * 150.0  # type: ignore[assignment]
            items_moved += 1

        return {"items_moved": items_moved, "edges_added": 0, "groups": []}
