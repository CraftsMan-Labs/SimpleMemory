from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateSourceRequest(BaseModel):
    source_type: str = Field(description="pdf, txt, md, url, etc.")
    title: str = Field(min_length=1, max_length=500)
    pipeline_id: str = Field(default="default_pdf_pipeline")
    uri: str | None = None
    metadata: dict = Field(default_factory=dict)


class PresignedUploadRequest(BaseModel):
    source_type: str
    title: str = Field(min_length=1, max_length=500)
    pipeline_id: str = Field(default="default_pdf_pipeline")
    metadata: dict = Field(default_factory=dict)


class ConfirmUploadRequest(BaseModel):
    source_id: uuid.UUID
    version_id: uuid.UUID


class CreateSourceResponse(BaseModel):
    source_id: uuid.UUID
    version_id: uuid.UUID
    job_id: uuid.UUID


class PresignedUploadResponse(BaseModel):
    source_id: uuid.UUID
    version_id: uuid.UUID
    upload_url: str
    expires_in: int


class ConfirmUploadResponse(BaseModel):
    job_id: uuid.UUID
    status: str


class SourceResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    source_type: str
    title: str
    uri: str | None
    content_hash: str | None
    status: str
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SourceListResponse(BaseModel):
    sources: list[SourceResponse]
    total: int


class SourceVersionResponse(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    parser_version: str | None
    raw_object_key: str
    content_hash: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    stage: str | None
    progress: float
    error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
