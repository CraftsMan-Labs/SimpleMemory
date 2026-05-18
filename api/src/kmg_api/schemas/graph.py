from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class GraphNodeResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    node_type: str
    canonical_name: str
    description: str | None
    aliases: list[str]
    confidence: float
    status: str
    primary_wiki_page_id: uuid.UUID | None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GraphNodeListResponse(BaseModel):
    nodes: list[GraphNodeResponse]
    total: int


class GraphEdgeResponse(BaseModel):
    id: uuid.UUID
    subject_type: str
    subject_id: uuid.UUID
    predicate: str
    object_type: str
    object_id: uuid.UUID
    confidence: float
    weight: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GraphEdgeListResponse(BaseModel):
    edges: list[GraphEdgeResponse]
    total: int


class GraphExploreResponse(BaseModel):
    center_node: GraphNodeResponse
    edges: list[GraphEdgeResponse]
    connected_nodes: list[GraphNodeResponse]
