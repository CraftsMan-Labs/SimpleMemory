from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.job import IngestionJob
from kmg_shared.repositories.base_repo import BaseRepository


class JobRepository(BaseRepository[IngestionJob]):
    model = IngestionJob

    async def create(
        self,
        source_id: uuid.UUID,
        source_version_id: uuid.UUID,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        pipeline_id: str,
    ) -> IngestionJob:
        job = IngestionJob(
            source_id=source_id,
            source_version_id=source_version_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            pipeline_id=pipeline_id,
        )
        self._session.add(job)
        await self._session.flush()
        return job

    async def update_status(
        self,
        job_id: uuid.UUID,
        status: str,
        *,
        stage: str | None = None,
        progress: float | None = None,
        error: str | None = None,
    ) -> None:
        values: dict[str, Any] = {"status": status}
        if stage is not None:
            values["stage"] = stage
        if progress is not None:
            values["progress"] = progress
        if error is not None:
            values["error"] = error

        stmt = update(IngestionJob).where(IngestionJob.id == job_id).values(**values)
        await self._session.execute(stmt)

    async def get_active_for_source(self, source_id: uuid.UUID) -> list[IngestionJob]:
        stmt = select(IngestionJob).where(
            IngestionJob.source_id == source_id,
            IngestionJob.status.in_(["queued", "running"]),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
