from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from kmg_api.dependencies import DbSession, TenantId, get_workspace_service
from kmg_api.schemas.workspace import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    WorkspaceListResponse,
    WorkspaceResponse,
)
from kmg_shared.db.models.workspace import Workspace
from kmg_shared.services import WorkspaceService

router = APIRouter(prefix="/v1/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    body: CreateWorkspaceRequest,
    tenant_id: TenantId,
    ws_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> Workspace:
    return await ws_service.create_workspace(
        tenant_id, name=body.name, slug=body.slug, settings=body.settings
    )


@router.get("", response_model=WorkspaceListResponse)
async def list_workspaces(
    tenant_id: TenantId,
    ws_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> dict:
    workspaces = await ws_service.list_workspaces(tenant_id)
    return {"workspaces": workspaces, "total": len(workspaces)}


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: uuid.UUID,
    tenant_id: TenantId,
    ws_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> Workspace:
    return await ws_service.get_workspace(tenant_id, workspace_id)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: uuid.UUID,
    body: UpdateWorkspaceRequest,
    tenant_id: TenantId,
    ws_service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> Workspace:
    return await ws_service.update_workspace(
        tenant_id, workspace_id, name=body.name, settings=body.settings
    )
