from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateCanvasRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    layout: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class UpdateCanvasRequest(BaseModel):
    title: str | None = None
    layout: dict | None = None


class CanvasItemRequest(BaseModel):
    item_type: str
    target_id: uuid.UUID | None = None
    x: float = 0.0
    y: float = 0.0
    width: float = 200.0
    height: float = 100.0
    style: dict = Field(default_factory=dict)


class CanvasEdgeRequest(BaseModel):
    from_item_id: uuid.UUID
    to_item_id: uuid.UUID
    label: str | None = None
    edge_type: str | None = None
    style: dict = Field(default_factory=dict)


class CanvasResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    layout: dict
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CanvasItemResponse(BaseModel):
    id: uuid.UUID
    canvas_id: uuid.UUID
    item_type: str
    target_id: uuid.UUID | None
    x: float
    y: float
    width: float
    height: float
    style: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class CanvasEdgeResponse(BaseModel):
    id: uuid.UUID
    canvas_id: uuid.UUID
    from_item_id: uuid.UUID
    to_item_id: uuid.UUID
    label: str | None
    edge_type: str | None
    style: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class CanvasDetailResponse(BaseModel):
    canvas: CanvasResponse
    items: list[CanvasItemResponse]
    edges: list[CanvasEdgeResponse]


class CanvasListResponse(BaseModel):
    canvases: list[CanvasResponse]
    total: int


class AiOrganizeResponse(BaseModel):
    items_moved: int
    edges_added: int
    groups: list[dict] = Field(default_factory=list)
