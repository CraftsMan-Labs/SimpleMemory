from __future__ import annotations

import uuid

from fastapi import APIRouter

from kmg_api.dependencies import DbSession, TenantId
from kmg_api.schemas.source import JobStatusResponse
from kmg_shared.errors import NotFoundError
from kmg_shared.repositories.job_repo import JobRepository

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job(
    job_id: uuid.UUID,
    tenant_id: TenantId,
    session: DbSession,
) -> object:
    repo = JobRepository(session)
    job = await repo.get_by_id(job_id)
    if job is None or job.tenant_id != tenant_id:
        raise NotFoundError("IngestionJob", job_id)
    return job
