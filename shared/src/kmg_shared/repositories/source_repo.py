from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.source import Source, SourceVersion
from kmg_shared.repositories.base_repo import BaseRepository


class SourceRepository(BaseRepository[Source]):
    model = Source

    async def create(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        source_type: str,
        title: str,
        *,
        uri: str | None = None,
        content_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Source:
        source = Source(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_type=source_type,
            title=title,
            uri=uri,
            content_hash=content_hash,
            metadata=metadata or {},
        )
        self._session.add(source)
        await self._session.flush()
        return source

    async def create_version(
        self,
        source_id: uuid.UUID,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        raw_object_key: str,
        *,
        parser_version: str | None = None,
        content_hash: str | None = None,
    ) -> SourceVersion:
        version = SourceVersion(
            source_id=source_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            raw_object_key=raw_object_key,
            parser_version=parser_version,
            content_hash=content_hash,
        )
        self._session.add(version)
        await self._session.flush()
        return version

    async def get_versions(self, source_id: uuid.UUID) -> list[SourceVersion]:
        stmt = (
            select(SourceVersion)
            .where(SourceVersion.source_id == source_id)
            .order_by(SourceVersion.created_at)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_version(self, source_id: uuid.UUID) -> SourceVersion | None:
        stmt = (
            select(SourceVersion)
            .where(SourceVersion.source_id == source_id)
            .order_by(SourceVersion.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, source_id: uuid.UUID, status: str) -> None:
        stmt = update(Source).where(Source.id == source_id).values(status=status)
        await self._session.execute(stmt)
