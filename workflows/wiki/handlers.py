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
from kmg_shared.repositories.wiki_repo import WikiRepository

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


def persist_wiki(context: dict, payload: dict) -> dict:
    """Persist wiki pages, revisions, evidence, links, and backlinks to Postgres."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="persist_wiki", tenant_id=payload.get("tenant_id"),
                          workspace_id=payload.get("workspace_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        tenant_id = uuid.UUID(payload["tenant_id"])
        workspace_id = uuid.UUID(payload["workspace_id"])
        source_id = uuid.UUID(payload["source_id"])
        source_version_id = uuid.UUID(payload["source_version_id"])
        wiki_pages_data: list[dict] = payload["wiki_pages"]
        wiki_links_data: list[dict] = payload["wiki_links"]

        wiki_page_ids: list[str] = []
        wiki_link_ids: list[str] = []
        backlink_count = 0

        async with session_factory() as session:
            repo = WikiRepository(session)
            slug_to_page_id: dict[str, uuid.UUID] = {}

            for page_data in wiki_pages_data:
                existing = await repo.get_page_by_slug(workspace_id, page_data["slug"])
                if existing:
                    page = await repo.update_page(
                        existing.id,
                        markdown=page_data["markdown"],
                        summary=page_data.get("summary"),
                    )
                    slug_to_page_id[page_data["slug"]] = existing.id
                    wiki_page_ids.append(str(existing.id))
                    log.info("wiki_page_updated", slug=page_data["slug"])
                else:
                    page = await repo.create_page(
                        tenant_id=tenant_id,
                        workspace_id=workspace_id,
                        slug=page_data["slug"],
                        title=page_data["title"],
                        page_type=page_data["page_type"],
                        markdown=page_data["markdown"],
                        summary=page_data.get("summary"),
                    )
                    slug_to_page_id[page_data["slug"]] = page.id
                    wiki_page_ids.append(str(page.id))

                md_hash = hashlib.sha256(page_data["markdown"].encode()).hexdigest()[:16]
                await repo.create_revision(
                    wiki_page_id=slug_to_page_id[page_data["slug"]],
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    revision_number=1,
                    markdown=page_data["markdown"],
                    author_type="ai",
                    markdown_hash=md_hash,
                    change_summary="Initial generation from source ingestion",
                )

                evidence_records = []
                for chunk_id in page_data.get("evidence_chunk_ids", []):
                    evidence_records.append({
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "wiki_page_id": slug_to_page_id[page_data["slug"]],
                        "chunk_id": uuid.UUID(chunk_id),
                        "confidence": page_data.get("confidence", 0.8),
                        "evidence_type": "generated_from",
                    })
                if evidence_records:
                    await repo.create_evidence_batch(evidence_records)

            link_records: list[dict[str, Any]] = []
            backlink_records: list[dict[str, Any]] = []
            for link_data in wiki_links_data:
                from_page_id = slug_to_page_id.get(link_data["from_slug"])
                to_page_id = slug_to_page_id.get(link_data["to_slug"])
                if not from_page_id or not to_page_id:
                    continue
                link_id = uuid.uuid4()
                link_records.append({
                    "id": link_id,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "from_page_id": from_page_id,
                    "to_page_id": to_page_id,
                    "link_text": link_data["link_text"],
                    "link_type": link_data["link_type"],
                    "confidence": link_data.get("confidence", 0.8),
                })
                wiki_link_ids.append(str(link_id))

                backlink_records.append({
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "wiki_page_id": to_page_id,
                    "source_page_id": from_page_id,
                    "link_text": link_data["link_text"],
                })

            if link_records:
                await repo.create_links_batch(link_records)
            if backlink_records:
                await repo.create_backlinks_batch(backlink_records)
                backlink_count = len(backlink_records)

            await session.commit()

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 page_count=len(wiki_page_ids), link_count=len(wiki_link_ids))
        return {
            "wiki_page_ids": wiki_page_ids,
            "wiki_link_ids": wiki_link_ids,
            "backlink_count": backlink_count,
        }

    return _run_async(_impl())


def embed_wiki(context: dict, payload: dict) -> dict:
    """Embed wiki pages and upsert to Qdrant with record_type='wiki_page'."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="embed_wiki", tenant_id=payload.get("tenant_id"),
                          workspace_id=payload.get("workspace_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        embedding = get_embedding()
        vector_db = get_vector_db()
        tenant_id = payload["tenant_id"]
        workspace_id = payload["workspace_id"]
        wiki_page_ids = payload["wiki_page_ids"]

        if not wiki_page_ids:
            log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                     vectors_upserted=0)
            return {"vectors_upserted": 0}

        from kmg_shared.db.models.wiki import WikiPage
        from sqlalchemy import select

        async with session_factory() as session:
            stmt = select(WikiPage).where(
                WikiPage.id.in_([uuid.UUID(pid) for pid in wiki_page_ids])
            )
            result = await session.execute(stmt)
            pages = list(result.scalars().all())

        now = datetime.now(timezone.utc).isoformat()
        records: list[VectorRecord] = []
        failed_ids: list[str] = []

        for page in pages:
            try:
                text = f"{page.title}\n\n{page.summary or ''}\n\n{page.markdown}"
                vectors = await embedding.embed_texts([text])
                vector = vectors[0]
                content_hash = hashlib.sha256(page.markdown.encode()).hexdigest()[:16]
                records.append(VectorRecord(
                    id=str(page.id),
                    vector=vector,
                    payload={
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "record_type": "wiki_page",
                        "record_id": str(page.id),
                        "status": "active",
                        "content_hash": content_hash,
                        "semantic_hash": content_hash,
                        "schema_version": 1,
                        "embedding_model": embedding.model_name,
                        "embedding_version": "1",
                        "created_at": now,
                        "updated_at": now,
                        "slug": page.slug,
                        "title": page.title,
                        "page_type": page.page_type,
                        "summary": page.summary or "",
                    },
                ))
            except Exception:
                failed_ids.append(str(page.id))
                log.warning("embed_wiki_page_failed", page_id=str(page.id), exc_info=True)

        upserted = 0
        if records:
            upserted = await vector_db.upsert(tenant_id, workspace_id, "wiki_page", records)

        if failed_ids:
            log.warning("partial_embed_failures", failed_count=len(failed_ids), failed_ids=failed_ids)

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 vectors_upserted=upserted, failed_count=len(failed_ids))
        return {"vectors_upserted": upserted, "failed_count": len(failed_ids), "failed_ids": failed_ids}

    return _run_async(_impl())
