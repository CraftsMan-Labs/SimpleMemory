from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

import structlog

from kmg_shared.infra.registry import get_db_session
from kmg_shared.repositories.canvas_repo import CanvasRepository

logger = structlog.get_logger()


def _run_async(coro):
    """Run an async coroutine from a sync SimpleAgents handler."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def load_canvas_items(context: dict, payload: dict) -> dict:
    """Load current canvas items and edges."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="load_canvas_items", canvas_id=payload.get("canvas_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        canvas_id = uuid.UUID(payload["canvas_id"])

        async with session_factory() as session:
            repo = CanvasRepository(session)
            canvas, items, edges = await repo.get_with_items(canvas_id)

        items_data = [
            {
                "id": str(item.id),
                "item_type": getattr(item, "item_type", "note"),
                "title": getattr(item, "title", ""),
                "x": getattr(item, "x", 0),
                "y": getattr(item, "y", 0),
                "width": getattr(item, "width", 200),
                "height": getattr(item, "height", 100),
            }
            for item in items
        ]

        edges_data = [
            {
                "id": str(edge.id),
                "from_item_id": str(getattr(edge, "from_item_id", "")),
                "to_item_id": str(getattr(edge, "to_item_id", "")),
                "label": getattr(edge, "label", ""),
            }
            for edge in edges
        ]

        current_layout = canvas.layout or {}

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 item_count=len(items_data), edge_count=len(edges_data))
        return {
            "items": items_data,
            "edges": edges_data,
            "current_layout": current_layout,
        }

    return _run_async(_impl())


def apply_layout(context: dict, payload: dict) -> dict:
    """Apply proposed layout changes to the canvas."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="apply_layout", canvas_id=payload.get("canvas_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        canvas_id = uuid.UUID(payload["canvas_id"])
        groups: list[dict] = payload["groups"]
        suggested_edges: list[dict] = payload["suggested_edges"]

        items_moved = 0
        edges_added = 0

        async with session_factory() as session:
            repo = CanvasRepository(session)

            layout: dict[str, Any] = {
                "groups": [
                    {
                        "label": g["label"],
                        "item_ids": g["item_ids"],
                        "x": g["x"],
                        "y": g["y"],
                    }
                    for g in groups
                ],
                "auto_organized": True,
            }
            await repo.update_layout(canvas_id, layout)
            items_moved = sum(len(g.get("item_ids", [])) for g in groups)

            if suggested_edges:
                edge_records = [
                    {
                        "from_item_id": uuid.UUID(e["from_id"]),
                        "to_item_id": uuid.UUID(e["to_id"]),
                        "label": e.get("label", ""),
                        "edge_type": "suggested",
                    }
                    for e in suggested_edges
                ]
                await repo.add_edges_batch(canvas_id, edge_records)
                edges_added = len(edge_records)

            await session.commit()

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 items_moved=items_moved, edges_added=edges_added)
        return {"items_moved": items_moved, "edges_added": edges_added}

    return _run_async(_impl())
