from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateWorkspaceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*$")
    settings: dict = Field(default_factory=lambda: {
        "default_pipeline_id": "default_pdf_pipeline",
        "visibility": "private",
        "wiki_style": "obsidian_like",
        "graph_mode": "wiki_first",
    })


class UpdateWorkspaceRequest(BaseModel):
    name: str | None = None
    settings: dict | None = None


class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    slug: str
    status: str
    settings: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceListResponse(BaseModel):
    workspaces: list[WorkspaceResponse]
    total: int
