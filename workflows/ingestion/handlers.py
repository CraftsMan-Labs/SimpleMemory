from __future__ import annotations

import asyncio
import hashlib
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import structlog

from kmg_shared.infra.registry import get_db_session, get_embedding, get_storage, get_vector_db
from kmg_shared.ports.vector_db import VectorRecord
from kmg_shared.repositories.chunk_repo import ChunkRepository
from kmg_shared.repositories.source_repo import SourceRepository

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


CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


def parse_source(context: dict, payload: dict) -> dict:
    """Read raw source from object storage and parse based on source_type."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="parse_source", tenant_id=payload.get("tenant_id"),
                          source_id=payload.get("source_id"))
        log.info("handler_started")

        storage = get_storage()
        source_version_id = payload["source_version_id"]
        source_type = payload["source_type"]

        object_key = f"sources/{payload['tenant_id']}/{payload['source_id']}/{source_version_id}/raw"
        raw_bytes = await storage.get(object_key)

        raw_text = ""
        page_count = 1
        meta: dict[str, Any] = {"source_type": source_type}

        if source_type in ("txt", "md"):
            raw_text = raw_bytes.decode("utf-8")
        elif source_type == "pdf":
            raw_text = raw_bytes.decode("utf-8", errors="replace")
            page_count = max(1, raw_text.count("\f") + 1)
        elif source_type == "url":
            raw_text = raw_bytes.decode("utf-8")
        else:
            raw_text = raw_bytes.decode("utf-8", errors="replace")

        meta["char_count"] = len(raw_text)
        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 char_count=meta["char_count"])
        return {"raw_text": raw_text, "page_count": page_count, "metadata": meta}

    return _run_async(_impl())


def segment_source(context: dict, payload: dict) -> dict:
    """Split raw_text into document segments by structure."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="segment_source", tenant_id=payload.get("tenant_id"),
                          source_id=payload.get("source_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        raw_text: str = payload["raw_text"]
        tenant_id = uuid.UUID(payload["tenant_id"])
        workspace_id = uuid.UUID(payload["workspace_id"])
        source_id = uuid.UUID(payload["source_id"])
        source_version_id = uuid.UUID(payload["source_version_id"])

        heading_pattern = re.compile(r"^(#{1,6}\s.+|[A-Z][A-Za-z0-9 ]{2,}(?:\n[=\-]{3,}))$", re.MULTILINE)
        splits = heading_pattern.split(raw_text)

        if len(splits) <= 1:
            segments_text = [
                raw_text[i : i + 2000]
                for i in range(0, len(raw_text), 2000)
            ]
        else:
            segments_text = [s.strip() for s in splits if s.strip()]

        segment_ids: list[str] = []
        async with session_factory() as session:
            repo = ChunkRepository(session)
            for ordinal, seg_text in enumerate(segments_text):
                text_hash = hashlib.sha256(seg_text.encode()).hexdigest()[:16]
                segment = await repo.create_segment(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    source_id=source_id,
                    source_version_id=source_version_id,
                    segment_type="heading",
                    segment_key=f"seg-{ordinal}",
                    ordinal=ordinal,
                    text_hash=text_hash,
                    metadata={"char_count": len(seg_text), "text_preview": seg_text[:200]},
                )
                segment_ids.append(str(segment.id))
            await session.commit()

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 segment_count=len(segment_ids))
        return {"segment_count": len(segment_ids), "segment_ids": segment_ids}

    return _run_async(_impl())


def create_chunks(context: dict, payload: dict) -> dict:
    """Break segments into overlapping chunks and persist to Postgres."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="create_chunks", tenant_id=payload.get("tenant_id"),
                          source_id=payload.get("source_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        tenant_id = uuid.UUID(payload["tenant_id"])
        workspace_id = uuid.UUID(payload["workspace_id"])
        source_id = uuid.UUID(payload["source_id"])
        source_version_id = uuid.UUID(payload["source_version_id"])
        segment_ids = payload["segment_ids"]

        async with session_factory() as session:
            repo = ChunkRepository(session)

            all_segments = []
            for seg_id in segment_ids:
                from kmg_shared.db.models.document import DocumentSegment
                from sqlalchemy import select

                stmt = select(DocumentSegment).where(DocumentSegment.id == uuid.UUID(seg_id))
                result = await session.execute(stmt)
                seg = result.scalar_one_or_none()
                if seg:
                    all_segments.append(seg)

            chunk_data_list: list[dict[str, Any]] = []
            chunk_index = 0
            skipped = 0
            for seg in all_segments:
                seg_text = seg.metadata.get("text_preview", "")
                if not seg_text:
                    continue
                start = 0
                while start < len(seg_text):
                    end = min(start + CHUNK_SIZE, len(seg_text))
                    chunk_text = seg_text[start:end]
                    text_hash = hashlib.sha256(chunk_text.encode()).hexdigest()[:16]

                    existing = await repo.find_by_hash_and_segment(text_hash, seg.id)
                    if existing:
                        skipped += 1
                        start += CHUNK_SIZE - CHUNK_OVERLAP
                        continue

                    chunk_data_list.append({
                        "id": uuid.uuid4(),
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "source_id": source_id,
                        "source_version_id": source_version_id,
                        "segment_id": seg.id,
                        "chunk_index": chunk_index,
                        "content": chunk_text,
                        "token_count": len(chunk_text) // 4,
                        "text_hash": text_hash,
                        "metadata": {},
                    })
                    chunk_index += 1
                    start += CHUNK_SIZE - CHUNK_OVERLAP

            chunks = await repo.create_chunks_batch(chunk_data_list)
            chunk_ids = [str(c.id) for c in chunks]
            await session.commit()

        if skipped:
            log.info("chunks_skipped_idempotent", skipped=skipped)
        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 chunk_count=len(chunk_ids))
        return {"chunk_count": len(chunk_ids), "chunk_ids": chunk_ids}

    return _run_async(_impl())


def embed_chunks(context: dict, payload: dict) -> dict:
    """Generate embeddings for chunks and upsert to Qdrant."""

    async def _impl():
        t0 = time.perf_counter()
        log = logger.bind(handler="embed_chunks", tenant_id=payload.get("tenant_id"),
                          workspace_id=payload.get("workspace_id"))
        log.info("handler_started")

        session_factory = get_db_session()
        embedding = get_embedding()
        vector_db = get_vector_db()
        tenant_id = payload["tenant_id"]
        workspace_id = payload["workspace_id"]
        chunk_ids = payload["chunk_ids"]

        async with session_factory() as session:
            repo = ChunkRepository(session)
            chunks = await repo.get_by_ids([uuid.UUID(cid) for cid in chunk_ids])

        if not chunks:
            log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                     vectors_upserted=0)
            return {"vectors_upserted": 0}

        now = datetime.now(timezone.utc).isoformat()
        records: list[VectorRecord] = []
        failed_ids: list[str] = []

        for chunk in chunks:
            try:
                vectors = await embedding.embed_texts([chunk.content])
                vector = vectors[0]
                content_hash = hashlib.sha256(chunk.content.encode()).hexdigest()[:16]
                records.append(VectorRecord(
                    id=str(chunk.id),
                    vector=vector,
                    payload={
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "record_type": "chunk",
                        "record_id": str(chunk.id),
                        "status": "active",
                        "content_hash": content_hash,
                        "semantic_hash": content_hash,
                        "schema_version": 1,
                        "embedding_model": embedding.model_name,
                        "embedding_version": "1",
                        "created_at": now,
                        "updated_at": now,
                        "source_id": str(chunk.source_id),
                        "chunk_index": chunk.chunk_index,
                        "content_preview": chunk.content[:200],
                    },
                ))
            except Exception:
                failed_ids.append(str(chunk.id))
                log.warning("embed_chunk_failed", chunk_id=str(chunk.id), exc_info=True)

        upserted = 0
        if records:
            upserted = await vector_db.upsert(tenant_id, workspace_id, "chunk", records)

        if failed_ids:
            log.warning("partial_embed_failures", failed_count=len(failed_ids), failed_ids=failed_ids)

        log.info("handler_completed", duration_s=round(time.perf_counter() - t0, 4),
                 vectors_upserted=upserted, failed_count=len(failed_ids))
        return {"vectors_upserted": upserted, "failed_count": len(failed_ids), "failed_ids": failed_ids}

    return _run_async(_impl())
