from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.canvas import WikiCanvas, WikiCanvasEdge, WikiCanvasItem
from kmg_shared.repositories.base_repo import BaseRepository


class CanvasRepository(BaseRepository[WikiCanvas]):
    model = WikiCanvas

    async def create_canvas(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        title: str,
        *,
        layout: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WikiCanvas:
        canvas = WikiCanvas(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            title=title,
            layout=layout or {},
            metadata=metadata or {},
        )
        self._session.add(canvas)
        await self._session.flush()
        return canvas

    async def add_items_batch(
        self, canvas_id: uuid.UUID, items: list[dict[str, Any]]
    ) -> list[WikiCanvasItem]:
        objects = [WikiCanvasItem(canvas_id=canvas_id, **data) for data in items]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def add_edges_batch(
        self, canvas_id: uuid.UUID, edges: list[dict[str, Any]]
    ) -> list[WikiCanvasEdge]:
        objects = [WikiCanvasEdge(canvas_id=canvas_id, **data) for data in edges]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def update_layout(self, canvas_id: uuid.UUID, layout: dict[str, Any]) -> WikiCanvas:
        stmt = update(WikiCanvas).where(WikiCanvas.id == canvas_id).values(layout=layout)
        await self._session.execute(stmt)
        return await self.get_by_id_or_raise(canvas_id)

    async def get_with_items(
        self, canvas_id: uuid.UUID
    ) -> tuple[WikiCanvas, list[WikiCanvasItem], list[WikiCanvasEdge]]:
        canvas = await self.get_by_id_or_raise(canvas_id)

        items_stmt = select(WikiCanvasItem).where(WikiCanvasItem.canvas_id == canvas_id)
        items_result = await self._session.execute(items_stmt)
        items = list(items_result.scalars().all())

        edges_stmt = select(WikiCanvasEdge).where(WikiCanvasEdge.canvas_id == canvas_id)
        edges_result = await self._session.execute(edges_stmt)
        edges = list(edges_result.scalars().all())

        return canvas, items, edges
