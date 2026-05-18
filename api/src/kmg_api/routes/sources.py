from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from kmg_api.dependencies import (
    DbSession,
    TenantId,
    WorkspaceId,
    get_source_service,
)
from kmg_api.schemas.source import (
    ConfirmUploadRequest,
    ConfirmUploadResponse,
    CreateSourceRequest,
    CreateSourceResponse,
    JobStatusResponse,
    PresignedUploadRequest,
    PresignedUploadResponse,
    SourceListResponse,
    SourceResponse,
    SourceVersionResponse,
)
from kmg_shared.errors import NotFoundError
from kmg_shared.repositories.source_repo import SourceRepository
from kmg_shared.repositories.job_repo import JobRepository
from kmg_shared.services import SourceService

router = APIRouter(prefix="/v1/sources", tags=["sources"])


@router.post("", response_model=CreateSourceResponse, status_code=201)
async def create_source(
    body: CreateSourceRequest,
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    source_service: Annotated[SourceService, Depends(get_source_service)],
) -> dict:
    source, version, job = await source_service.create_source(
        tenant_id,
        workspace_id,
        source_type=body.source_type,
        title=body.title,
        pipeline_id=body.pipeline_id,
        uri=body.uri,
        metadata=body.metadata,
    )
    return {"source_id": source.id, "version_id": version.id, "job_id": job.id}


@router.post("/presigned", response_model=PresignedUploadResponse, status_code=201)
async def create_presigned_upload(
    body: PresignedUploadRequest,
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    source_service: Annotated[SourceService, Depends(get_source_service)],
) -> dict:
    source, version, upload_url = await source_service.create_presigned_upload(
        tenant_id,
        workspace_id,
        source_type=body.source_type,
        title=body.title,
        pipeline_id=body.pipeline_id,
        metadata=body.metadata,
    )
    return {
        "source_id": source.id,
        "version_id": version.id,
        "upload_url": upload_url,
        "expires_in": 3600,
    }


@router.post("/confirm", response_model=ConfirmUploadResponse)
async def confirm_upload(
    body: ConfirmUploadRequest,
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    source_service: Annotated[SourceService, Depends(get_source_service)],
) -> dict:
    job = await source_service.confirm_source_upload(
        tenant_id, workspace_id, body.source_id, body.version_id
    )
    return {"job_id": job.id, "status": "queued"}


@router.get("", response_model=SourceListResponse)
async def list_sources(
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    session: DbSession,
) -> dict:
    repo = SourceRepository(session)
    sources = await repo.list_by_workspace(tenant_id, workspace_id)
    total = await repo.count_by_workspace(tenant_id, workspace_id)
    return {"sources": sources, "total": total}


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: uuid.UUID,
    tenant_id: TenantId,
    session: DbSession,
) -> object:
    repo = SourceRepository(session)
    source = await repo.get_by_id(source_id)
    if source is None or source.tenant_id != tenant_id:
        raise NotFoundError("Source", source_id)
    return source


@router.get("/{source_id}/versions", response_model=list[SourceVersionResponse])
async def list_source_versions(
    source_id: uuid.UUID,
    tenant_id: TenantId,
    session: DbSession,
) -> list:
    repo = SourceRepository(session)
    source = await repo.get_by_id(source_id)
    if source is None or source.tenant_id != tenant_id:
        raise NotFoundError("Source", source_id)
    return await repo.get_versions(source_id)


@router.get("/{source_id}/jobs", response_model=list[JobStatusResponse])
async def list_source_jobs(
    source_id: uuid.UUID,
    tenant_id: TenantId,
    session: DbSession,
) -> list:
    job_repo = JobRepository(session)
    return await job_repo.get_active_for_source(source_id)
