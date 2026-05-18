from __future__ import annotations

import asyncio
import hashlib
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import structlog

from kmg_shared.infra.registry import get_db_session, get_embedding, get_vector_db
from kmg_shared.ports.vector_db import VectorRecord
from kmg_shared.repositories.graph_repo import GraphRepository

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


def deduplicate_nodes(context: dict, payload: dict) -> dict:
    """Check extracted entities against existing graph nodes, merge duplicates."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="deduplicate_nodes", workspace_id=payload.get("workspace_id"))
        log.info("handler_started", entity_count=len(payload.get("entities", [])))

        session_factory = get_db_session()
        workspace_id = uuid.UUID(payload["workspace_id"])
        entities: list[dict] = payload["entities"]

        node_proposals: list[dict] = []
        merged_count = 0

        async with session_factory() as session:
            repo = GraphRepository(session)

            for entity in entities:
                canonical = entity["canonical_name"]
                existing = await repo.find_by_canonical_name(workspace_id, canonical)

                if existing:
                    merged_count += 1
                    node_proposals.append({
                        "action": "merge",
                        "existing_node_id": str(existing.id),
                        "canonical_name": canonical,
                        "node_type": entity["node_type"],
                        "description": entity["description"],
                        "aliases": list(set((existing.aliases or []) + entity.get("aliases", []))),
                        "confidence": max(existing.confidence or 0, entity.get("confidence", 0.8)),
                        "evidence_chunk_ids": entity.get("evidence_chunk_ids", []),
                    })
                else:
                    aliases = entity.get("aliases", [])
                    found_by_alias = False
                    for alias in aliases:
                        existing_alias = await repo.find_by_canonical_name(workspace_id, alias)
                        if existing_alias:
                            merged_count += 1
                            node_proposals.append({
                                "action": "merge",
                                "existing_node_id": str(existing_alias.id),
                                "canonical_name": canonical,
                                "node_type": entity["node_type"],
                                "description": entity["description"],
                                "aliases": list(set((existing_alias.aliases or []) + aliases + [canonical])),
                                "confidence": max(existing_alias.confidence or 0, entity.get("confidence", 0.8)),
                                "evidence_chunk_ids": entity.get("evidence_chunk_ids", []),
                            })
                            found_by_alias = True
                            break

                    if not found_by_alias:
                        node_proposals.append({
                            "action": "create",
                            "canonical_name": canonical,
                            "node_type": entity["node_type"],
                            "description": entity["description"],
                            "aliases": aliases,
                            "confidence": entity.get("confidence", 0.8),
                            "evidence_chunk_ids": entity.get("evidence_chunk_ids", []),
                        })

        unique_count = sum(1 for p in node_proposals if p["action"] == "create")
        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 unique_count=unique_count, merged_count=merged_count)
        return {
            "unique_node_count": unique_count,
            "merged_count": merged_count,
            "node_proposals": node_proposals,
        }

    return _run_async(_impl())


def persist_graph(context: dict, payload: dict) -> dict:
    """Persist graph nodes, edges, and wiki_graph_links to Postgres."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="persist_graph", tenant_id=payload.get("tenant_id"),
                          workspace_id=payload.get("workspace_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        tenant_id = uuid.UUID(payload["tenant_id"])
        workspace_id = uuid.UUID(payload["workspace_id"])
        source_id = uuid.UUID(payload["source_id"])
        node_proposals: list[dict] = payload["node_proposals"]
        relations: list[dict] = payload["relations"]
        wiki_page_ids: list[str] = payload.get("wiki_page_ids", [])

        node_ids: list[str] = []
        edge_ids: list[str] = []
        wiki_graph_link_ids: list[str] = []
        name_to_node_id: dict[str, uuid.UUID] = {}
        edges_skipped = 0

        async with session_factory() as session:
            repo = GraphRepository(session)

            for proposal in node_proposals:
                if proposal["action"] == "create":
                    node = await repo.create_node(
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        node_type=proposal["node_type"],
                        canonical_name=proposal["canonical_name"],
                        description=proposal.get("description"),
                        aliases=proposal.get("aliases"),
                        confidence=proposal.get("confidence", 0.8),
                    )
                    node_ids.append(str(node.id))
                    name_to_node_id[proposal["canonical_name"]] = node.id
                else:
                    existing_id = uuid.UUID(proposal["existing_node_id"])
                    node_ids.append(str(existing_id))
                    name_to_node_id[proposal["canonical_name"]] = existing_id

            for relation in relations:
                subject_id = name_to_node_id.get(relation["subject_name"])
                object_id = name_to_node_id.get(relation["object_name"])
                if not subject_id or not object_id:
                    continue

                existing_edge = await repo.find_edge(
                    workspace_id, subject_id, relation["predicate"], object_id,
                )
                if existing_edge:
                    edges_skipped += 1
                    edge_ids.append(str(existing_edge.id))
                    continue

                evidence_chunk_ids = relation.get("evidence_chunk_ids", [])
                evidence_chunk_id = uuid.UUID(evidence_chunk_ids[0]) if evidence_chunk_ids else None

                edge = await repo.create_edge(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    subject_type="graph_node",
                    subject_id=subject_id,
                    predicate=relation["predicate"],
                    object_type="graph_node",
                    object_id=object_id,
                    confidence=relation.get("confidence", 0.8),
                    evidence_chunk_id=evidence_chunk_id,
                )
                edge_ids.append(str(edge.id))

            if wiki_page_ids:
                wiki_graph_links = []
                for wp_id in wiki_page_ids:
                    for node_id in node_ids[:5]:
                        wiki_graph_links.append({
                            "tenant_id": tenant_id,
                            "workspace_id": workspace_id,
                            "wiki_page_id": uuid.UUID(wp_id),
                            "graph_node_id": uuid.UUID(node_id),
                            "link_type": "describes",
                        })
                if wiki_graph_links:
                    links = await repo.create_wiki_graph_links_batch(wiki_graph_links)
                    wiki_graph_link_ids = [str(lnk.id) for lnk in links]

            await session.commit()

        if edges_skipped:
            log.info("edges_skipped_idempotent", skipped=edges_skipped)
        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 node_count=len(node_ids), edge_count=len(edge_ids))
        return {
            "node_ids": node_ids,
            "edge_ids": edge_ids,
            "wiki_graph_link_ids": wiki_graph_link_ids,
        }

    return _run_async(_impl())


def embed_graph_nodes(context: dict, payload: dict) -> dict:
    """Embed graph nodes and upsert to Qdrant with record_type='graph_node'."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="embed_graph_nodes", tenant_id=payload.get("tenant_id"),
                          workspace_id=payload.get("workspace_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        embedding = get_embedding()
        vector_db = get_vector_db()
        tenant_id = payload["tenant_id"]
        workspace_id = payload["workspace_id"]
        node_ids = payload["node_ids"]

        if not node_ids:
            log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                     vectors_upserted=0)
            return {"vectors_upserted": 0}

        from kmg_shared.db.models.graph import GraphNode
        from sqlalchemy import select

        async with session_factory() as session:
            stmt = select(GraphNode).where(
                GraphNode.id.in_([uuid.UUID(nid) for nid in node_ids])
            )
            result = await session.execute(stmt)
            nodes = list(result.scalars().all())

        now = datetime.now(timezone.utc).isoformat()
        records: list[VectorRecord] = []
        failed_ids: list[str] = []

        for node in nodes:
            try:
                text = f"{node.canonical_name}: {node.description or ''} (aliases: {', '.join(node.aliases or [])})"
                vectors = await embedding.embed_texts([text])
                vector = vectors[0]
                content = f"{node.canonical_name}: {node.description or ''}"
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                records.append(VectorRecord(
                    id=str(node.id),
                    vector=vector,
                    payload={
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "record_type": "graph_node",
                        "record_id": str(node.id),
                        "status": "active",
                        "content_hash": content_hash,
                        "semantic_hash": content_hash,
                        "schema_version": 1,
                        "embedding_model": embedding.model_name,
                        "embedding_version": "1",
                        "created_at": now,
                        "updated_at": now,
                        "canonical_name": node.canonical_name,
                        "node_type": node.node_type,
                        "description": node.description or "",
                        "aliases": node.aliases or [],
                    },
                ))
            except Exception:
                failed_ids.append(str(node.id))
                log.warning("embed_graph_node_failed", node_id=str(node.id), exc_info=True)

        upserted = 0
        if records:
            upserted = await vector_db.upsert(tenant_id, workspace_id, "graph_node", records)

        if failed_ids:
            log.warning("partial_embed_failures", failed_count=len(failed_ids), failed_ids=failed_ids)

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 vectors_upserted=upserted, failed_count=len(failed_ids))
        return {"vectors_upserted": upserted, "failed_count": len(failed_ids), "failed_ids": failed_ids}

    return _run_async(_impl())
