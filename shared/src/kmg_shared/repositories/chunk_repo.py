from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.document import Chunk, DocumentSegment
from kmg_shared.repositories.base_repo import BaseRepository


class ChunkRepository(BaseRepository[Chunk]):
    model = Chunk

    async def create_segment(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        source_id: uuid.UUID,
        source_version_id: uuid.UUID,
        segment_type: str,
        segment_key: str,
        ordinal: int,
        *,
        page_number: int | None = None,
        text_hash: str | None = None,
        semantic_hash: str | None = None,
        stable_anchor: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> DocumentSegment:
        segment = DocumentSegment(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_id=source_id,
            source_version_id=source_version_id,
            segment_type=segment_type,
            segment_key=segment_key,
            ordinal=ordinal,
            page_number=page_number,
            text_hash=text_hash,
            semantic_hash=semantic_hash,
            stable_anchor=stable_anchor,
            metadata=metadata or {},
        )
        self._session.add(segment)
        await self._session.flush()
        return segment

    async def create_chunks_batch(self, chunks: list[dict[str, Any]]) -> list[Chunk]:
        chunk_objects = [Chunk(**data) for data in chunks]
        self._session.add_all(chunk_objects)
        await self._session.flush()
        return chunk_objects

    async def get_by_source_version(self, source_version_id: uuid.UUID) -> list[Chunk]:
        stmt = (
            select(Chunk)
            .where(Chunk.source_version_id == source_version_id)
            .order_by(Chunk.chunk_index)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_ids(self, chunk_ids: list[uuid.UUID]) -> list[Chunk]:
        if not chunk_ids:
            return []
        stmt = select(Chunk).where(Chunk.id.in_(chunk_ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_hash_and_segment(
        self, text_hash: str, segment_id: uuid.UUID
    ) -> Chunk | None:
        stmt = select(Chunk).where(
            Chunk.text_hash == text_hash,
            Chunk.segment_id == segment_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
