from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from kmg_api.dependencies import TenantId, WorkspaceId, get_graph_service
from kmg_api.schemas.graph import (
    GraphEdgeListResponse,
    GraphExploreResponse,
    GraphNodeListResponse,
    GraphNodeResponse,
)
from kmg_shared.services import GraphService

router = APIRouter(prefix="/v1/graph", tags=["graph"])


@router.get("/nodes", response_model=GraphNodeListResponse)
async def list_graph_nodes(
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    graph_service: Annotated[GraphService, Depends(get_graph_service)],
) -> dict:
    nodes, total = await graph_service.list_nodes(tenant_id, workspace_id)
    return {"nodes": nodes, "total": total}


@router.get("/nodes/{node_id}", response_model=GraphNodeResponse)
async def get_graph_node(
    node_id: uuid.UUID,
    tenant_id: TenantId,
    graph_service: Annotated[GraphService, Depends(get_graph_service)],
) -> object:
    return await graph_service.get_node(tenant_id, node_id)


@router.get("/nodes/{node_id}/edges", response_model=GraphEdgeListResponse)
async def get_node_edges(
    node_id: uuid.UUID,
    tenant_id: TenantId,
    graph_service: Annotated[GraphService, Depends(get_graph_service)],
) -> dict:
    node = await graph_service.get_node(tenant_id, node_id)
    from kmg_shared.db.models.graph import GraphEdge
    from sqlalchemy import or_, select

    stmt = select(GraphEdge).where(
        GraphEdge.tenant_id == tenant_id,
        or_(
            GraphEdge.subject_id == node_id,
            GraphEdge.object_id == node_id,
        ),
    )
    result = await graph_service._graph_repo._session.execute(stmt)
    edges = list(result.scalars().all())
    return {"edges": edges, "total": len(edges)}


@router.get("/nodes/{node_id}/explore", response_model=GraphExploreResponse)
async def explore_node(
    node_id: uuid.UUID,
    tenant_id: TenantId,
    graph_service: Annotated[GraphService, Depends(get_graph_service)],
) -> dict:
    return await graph_service.explore_node(tenant_id, node_id)


@router.get("/edges", response_model=GraphEdgeListResponse)
async def list_graph_edges(
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    graph_service: Annotated[GraphService, Depends(get_graph_service)],
) -> dict:
    edges = await graph_service.list_edges(tenant_id, workspace_id)
    return {"edges": edges, "total": len(edges)}
