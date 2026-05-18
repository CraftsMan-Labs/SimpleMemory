from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from kmg_api.dependencies import TenantId, WorkspaceId, get_canvas_service
from kmg_api.schemas.canvas import (
    AiOrganizeResponse,
    CanvasDetailResponse,
    CanvasEdgeRequest,
    CanvasEdgeResponse,
    CanvasItemRequest,
    CanvasItemResponse,
    CanvasListResponse,
    CanvasResponse,
    CreateCanvasRequest,
    UpdateCanvasRequest,
)
from kmg_shared.services import CanvasService

router = APIRouter(prefix="/v1/canvases", tags=["canvases"])


@router.post("", response_model=CanvasResponse, status_code=201)
async def create_canvas(
    body: CreateCanvasRequest,
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    canvas_service: Annotated[CanvasService, Depends(get_canvas_service)],
) -> object:
    return await canvas_service.create_canvas(
        tenant_id, workspace_id, title=body.title, layout=body.layout, metadata=body.metadata
    )


@router.get("", response_model=CanvasListResponse)
async def list_canvases(
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    canvas_service: Annotated[CanvasService, Depends(get_canvas_service)],
) -> dict:
    canvases, total = await canvas_service.list_canvases(tenant_id, workspace_id)
    return {"canvases": canvases, "total": total}


@router.get("/{canvas_id}", response_model=CanvasDetailResponse)
async def get_canvas(
    canvas_id: uuid.UUID,
    tenant_id: TenantId,
    canvas_service: Annotated[CanvasService, Depends(get_canvas_service)],
) -> dict:
    canvas, items, edges = await canvas_service.get_canvas(tenant_id, canvas_id)
    return {"canvas": canvas, "items": items, "edges": edges}


@router.patch("/{canvas_id}", response_model=CanvasResponse)
async def update_canvas(
    canvas_id: uuid.UUID,
    body: UpdateCanvasRequest,
    tenant_id: TenantId,
    canvas_service: Annotated[CanvasService, Depends(get_canvas_service)],
) -> object:
    return await canvas_service.update_canvas(
        tenant_id, canvas_id, title=body.title, layout=body.layout
    )


@router.delete("/{canvas_id}", status_code=204)
async def delete_canvas(
    canvas_id: uuid.UUID,
    tenant_id: TenantId,
    canvas_service: Annotated[CanvasService, Depends(get_canvas_service)],
) -> None:
    await canvas_service.delete_canvas(tenant_id, canvas_id)


@router.post("/{canvas_id}/items", response_model=list[CanvasItemResponse], status_code=201)
async def add_canvas_items(
    canvas_id: uuid.UUID,
    items: list[CanvasItemRequest],
    tenant_id: TenantId,
    canvas_service: Annotated[CanvasService, Depends(get_canvas_service)],
) -> list:
    item_dicts = [
        {
            "item_type": item.item_type,
            "target_id": item.target_id,
            "x": item.x,
            "y": item.y,
            "width": item.width,
            "height": item.height,
            "style": item.style,
        }
        for item in items
    ]
    return await canvas_service.add_items(tenant_id, canvas_id, item_dicts)


@router.post("/{canvas_id}/edges", response_model=list[CanvasEdgeResponse], status_code=201)
async def add_canvas_edges(
    canvas_id: uuid.UUID,
    edges: list[CanvasEdgeRequest],
    tenant_id: TenantId,
    canvas_service: Annotated[CanvasService, Depends(get_canvas_service)],
) -> list:
    edge_dicts = [
        {
            "from_item_id": edge.from_item_id,
            "to_item_id": edge.to_item_id,
            "label": edge.label,
            "edge_type": edge.edge_type,
            "style": edge.style,
        }
        for edge in edges
    ]
    return await canvas_service.add_edges(tenant_id, canvas_id, edge_dicts)


@router.post("/{canvas_id}/ai-organize", response_model=AiOrganizeResponse)
async def ai_organize_canvas(
    canvas_id: uuid.UUID,
    tenant_id: TenantId,
    canvas_service: Annotated[CanvasService, Depends(get_canvas_service)],
) -> dict:
    return await canvas_service.ai_organize(tenant_id, canvas_id)
