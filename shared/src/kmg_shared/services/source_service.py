from __future__ import annotations

import uuid
from typing import Any

from kmg_shared.db.models.job import IngestionJob
from kmg_shared.db.models.source import Source, SourceVersion
from kmg_shared.errors import NotFoundError, SourceUploadNotFoundError
from kmg_shared.ports.queue import JobQueue
from kmg_shared.ports.storage import ObjectStorage
from kmg_shared.repositories.job_repo import JobRepository
from kmg_shared.repositories.source_repo import SourceRepository


class SourceService:
    def __init__(
        self,
        source_repo: SourceRepository,
        job_repo: JobRepository,
        storage: ObjectStorage,
        queue: JobQueue,
    ) -> None:
        self._source_repo = source_repo
        self._job_repo = job_repo
        self._storage = storage
        self._queue = queue

    async def create_source(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        *,
        source_type: str,
        title: str,
        pipeline_id: str = "default_pdf_pipeline",
        uri: str | None = None,
        metadata: dict[str, Any] | None = None,
        raw_content: bytes | None = None,
    ) -> tuple[Source, SourceVersion, IngestionJob]:
        source = await self._source_repo.create(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_type=source_type,
            title=title,
            uri=uri,
            metadata=metadata,
        )

        object_key = f"sources/{tenant_id}/{workspace_id}/{source.id}/raw"
        version = await self._source_repo.create_version(
            source_id=source.id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            raw_object_key=object_key,
        )

        if raw_content:
            await self._storage.put(object_key, raw_content)

        job = await self._job_repo.create(
            source_id=source.id,
            source_version_id=version.id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            pipeline_id=pipeline_id,
        )

        await self._queue.enqueue(
            "ingestion",
            str(job.id),
            {
                "source_id": str(source.id),
                "version_id": str(version.id),
                "pipeline_id": pipeline_id,
            },
        )

        return source, version, job

    async def create_presigned_upload(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        *,
        source_type: str,
        title: str,
        pipeline_id: str = "default_pdf_pipeline",
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Source, SourceVersion, str]:
        source = await self._source_repo.create(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_type=source_type,
            title=title,
            metadata=metadata,
        )
        await self._source_repo.update_status(source.id, "pending_upload")

        object_key = f"sources/{tenant_id}/{workspace_id}/{source.id}/raw"
        version = await self._source_repo.create_version(
            source_id=source.id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            raw_object_key=object_key,
        )

        upload_url = await self._storage.presigned_url(
            object_key, expires_in=3600
        )
        return source, version, upload_url

    async def confirm_source_upload(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        source_id: uuid.UUID,
        version_id: uuid.UUID,
        *,
        pipeline_id: str = "default_pdf_pipeline",
    ) -> IngestionJob:
        source = await self._source_repo.get_by_id(source_id)
        if source is None or source.tenant_id != tenant_id:
            raise NotFoundError("Source", source_id)

        object_key = f"sources/{tenant_id}/{workspace_id}/{source_id}/raw"
        if not await self._storage.exists(object_key):
            raise SourceUploadNotFoundError(source_id, version_id)

        await self._source_repo.update_status(source_id, "active")

        job = await self._job_repo.create(
            source_id=source_id,
            source_version_id=version_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            pipeline_id=pipeline_id,
        )

        await self._queue.enqueue(
            "ingestion",
            str(job.id),
            {
                "source_id": str(source_id),
                "version_id": str(version_id),
                "pipeline_id": pipeline_id,
            },
        )

        return job
