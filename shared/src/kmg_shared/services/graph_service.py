from __future__ import annotations

import uuid

from sqlalchemy import select

from kmg_shared.db.models.graph import GraphEdge, GraphNode
from kmg_shared.errors import NotFoundError
from kmg_shared.repositories.graph_repo import GraphRepository


class GraphService:
    def __init__(self, graph_repo: GraphRepository) -> None:
        self._graph_repo = graph_repo

    async def list_nodes(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[GraphNode], int]:
        nodes = await self._graph_repo.list_by_workspace(
            tenant_id, workspace_id, limit=limit, offset=offset
        )
        total = await self._graph_repo.count_by_workspace(
            tenant_id, workspace_id
        )
        return nodes, total

    async def get_node(
        self, tenant_id: uuid.UUID, node_id: uuid.UUID
    ) -> GraphNode:
        node = await self._graph_repo.get_by_id(node_id)
        if node is None or node.tenant_id != tenant_id:
            raise NotFoundError("GraphNode", node_id)
        return node

    async def list_edges(
        self, tenant_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> list[GraphEdge]:
        stmt = select(GraphEdge).where(
            GraphEdge.tenant_id == tenant_id,
            GraphEdge.workspace_id == workspace_id,
            GraphEdge.status == "active",
        )
        result = await self._graph_repo._session.execute(stmt)
        return list(result.scalars().all())

    async def explore_node(
        self, tenant_id: uuid.UUID, node_id: uuid.UUID
    ) -> dict:
        node = await self.get_node(tenant_id, node_id)

        edges = await self._graph_repo.get_edges_for_node(node_id)
        # Filter edges by tenant_id
        edges = [e for e in edges if e.tenant_id == tenant_id]

        connected_ids: set[uuid.UUID] = set()
        for edge in edges:
            if edge.subject_id != node_id:
                connected_ids.add(edge.subject_id)
            if edge.object_id != node_id:
                connected_ids.add(edge.object_id)

        connected_nodes: list[GraphNode] = []
        if connected_ids:
            stmt = select(GraphNode).where(
                GraphNode.id.in_(connected_ids),
                GraphNode.tenant_id == tenant_id,
            )
            result = await self._graph_repo._session.execute(stmt)
            connected_nodes = list(result.scalars().all())

        return {
            "center_node": node,
            "edges": edges,
            "connected_nodes": connected_nodes,
        }
