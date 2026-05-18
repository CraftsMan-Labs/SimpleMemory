from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

import structlog

from kmg_shared.infra.registry import get_db_session, get_embedding, get_vector_db
from kmg_shared.repositories.chunk_repo import ChunkRepository

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


def vector_search(context: dict, payload: dict) -> dict:
    """Search Qdrant with query embedding, applying scope filters."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="vector_search", tenant_id=payload.get("tenant_id"),
                          workspace_id=payload.get("workspace_id"))
        log.info("handler_started")

        embedding_provider = get_embedding()
        vector_db = get_vector_db()

        tenant_id = payload["tenant_id"]
        workspace_id = payload["workspace_id"]
        refined_query = payload["refined_query"]
        record_types = payload["record_types"]
        limit = int(payload.get("limit", 20))
        intent = payload.get("intent", "factual")

        if intent == "exploratory":
            limit = min(limit * 2, 50)

        query_vector = await embedding_provider.embed_text(refined_query)

        scored_results = await vector_db.search(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            query_vector=query_vector,
            record_types=record_types,
            limit=limit,
        )

        results = [
            {
                "id": r.id,
                "score": r.score,
                "record_type": r.payload.get("record_type", "unknown"),
                "payload": r.payload,
            }
            for r in scored_results
        ]

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 total_found=len(results))
        return {"results": results, "total_found": len(results)}

    return _run_async(_impl())


def hydrate_results(context: dict, payload: dict) -> dict:
    """Fetch full records from Postgres for search results."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="hydrate_results")
        log.info("handler_started")

        session_factory = get_db_session()
        results: list[dict] = payload["results"]

        if not results:
            log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                     hydrated_count=0)
            return {"hydrated_results": []}

        chunks_to_fetch: list[uuid.UUID] = []
        wiki_pages_to_fetch: list[uuid.UUID] = []
        graph_nodes_to_fetch: list[uuid.UUID] = []

        for r in results:
            record_id = r["payload"].get("record_id", r["id"])
            record_type = r["record_type"]
            rid = uuid.UUID(record_id)
            if record_type == "chunk":
                chunks_to_fetch.append(rid)
            elif record_type == "wiki_page":
                wiki_pages_to_fetch.append(rid)
            elif record_type == "graph_node":
                graph_nodes_to_fetch.append(rid)

        hydrated: list[dict[str, Any]] = []

        async with session_factory() as session:
            if chunks_to_fetch:
                repo = ChunkRepository(session)
                chunks = await repo.get_by_ids(chunks_to_fetch)
                chunk_map = {str(c.id): c for c in chunks}
                for r in results:
                    if r["record_type"] == "chunk":
                        record_id = r["payload"].get("record_id", r["id"])
                        chunk = chunk_map.get(record_id)
                        if chunk:
                            hydrated.append({
                                "record_id": str(chunk.id),
                                "record_type": "chunk",
                                "title": f"Chunk #{chunk.chunk_index}",
                                "content": chunk.content,
                                "score": r["score"],
                                "source_id": str(chunk.source_id),
                            })

            if wiki_pages_to_fetch:
                from kmg_shared.db.models.wiki import WikiPage
                from sqlalchemy import select

                stmt = select(WikiPage).where(WikiPage.id.in_(wiki_pages_to_fetch))
                result = await session.execute(stmt)
                pages = {str(p.id): p for p in result.scalars().all()}
                for r in results:
                    if r["record_type"] == "wiki_page":
                        record_id = r["payload"].get("record_id", r["id"])
                        page = pages.get(record_id)
                        if page:
                            hydrated.append({
                                "record_id": str(page.id),
                                "record_type": "wiki_page",
                                "title": page.title,
                                "content": page.markdown[:2000],
                                "score": r["score"],
                                "slug": page.slug,
                            })

            if graph_nodes_to_fetch:
                from kmg_shared.db.models.graph import GraphNode
                from sqlalchemy import select

                stmt = select(GraphNode).where(GraphNode.id.in_(graph_nodes_to_fetch))
                result = await session.execute(stmt)
                nodes = {str(n.id): n for n in result.scalars().all()}
                for r in results:
                    if r["record_type"] == "graph_node":
                        record_id = r["payload"].get("record_id", r["id"])
                        node = nodes.get(record_id)
                        if node:
                            hydrated.append({
                                "record_id": str(node.id),
                                "record_type": "graph_node",
                                "title": node.canonical_name,
                                "content": node.description or "",
                                "score": r["score"],
                                "node_type": node.node_type,
                                "aliases": node.aliases or [],
                            })

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 hydrated_count=len(hydrated))
        return {"hydrated_results": hydrated}

    return _run_async(_impl())
