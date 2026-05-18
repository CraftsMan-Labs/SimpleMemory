from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.graph import GraphEdge, GraphNode, WikiGraphLink
from kmg_shared.repositories.base_repo import BaseRepository


class GraphRepository(BaseRepository[GraphNode]):
    model = GraphNode

    async def create_node(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        node_type: str,
        canonical_name: str,
        *,
        description: str | None = None,
        aliases: list[str] | None = None,
        confidence: float = 1.0,
        primary_wiki_page_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> GraphNode:
        node = GraphNode(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            node_type=node_type,
            canonical_name=canonical_name,
            description=description,
            aliases=aliases or [],
            confidence=confidence,
            primary_wiki_page_id=primary_wiki_page_id,
            metadata=metadata or {},
        )
        self._session.add(node)
        await self._session.flush()
        return node

    async def create_nodes_batch(self, nodes: list[dict[str, Any]]) -> list[GraphNode]:
        objects = [GraphNode(**data) for data in nodes]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def find_by_canonical_name(
        self, workspace_id: uuid.UUID, canonical_name: str
    ) -> GraphNode | None:
        stmt = select(GraphNode).where(
            GraphNode.workspace_id == workspace_id,
            GraphNode.canonical_name == canonical_name,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_edge(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        subject_type: str,
        subject_id: uuid.UUID,
        predicate: str,
        object_type: str,
        object_id: uuid.UUID,
        *,
        confidence: float = 1.0,
        weight: float = 1.0,
        evidence_chunk_id: uuid.UUID | None = None,
        evidence_wiki_page_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> GraphEdge:
        edge = GraphEdge(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            subject_type=subject_type,
            subject_id=subject_id,
            predicate=predicate,
            object_type=object_type,
            object_id=object_id,
            confidence=confidence,
            weight=weight,
            evidence_chunk_id=evidence_chunk_id,
            evidence_wiki_page_id=evidence_wiki_page_id,
            metadata=metadata or {},
        )
        self._session.add(edge)
        await self._session.flush()
        return edge

    async def create_edges_batch(self, edges: list[dict[str, Any]]) -> list[GraphEdge]:
        objects = [GraphEdge(**data) for data in edges]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def create_wiki_graph_links_batch(
        self, links: list[dict[str, Any]]
    ) -> list[WikiGraphLink]:
        objects = [WikiGraphLink(**data) for data in links]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def find_edge(
        self,
        workspace_id: uuid.UUID,
        subject_id: uuid.UUID,
        predicate: str,
        object_id: uuid.UUID,
    ) -> GraphEdge | None:
        stmt = select(GraphEdge).where(
            GraphEdge.workspace_id == workspace_id,
            GraphEdge.subject_id == subject_id,
            GraphEdge.predicate == predicate,
            GraphEdge.object_id == object_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_edges_for_node(self, node_id: uuid.UUID) -> list[GraphEdge]:
        stmt = select(GraphEdge).where(
            or_(
                GraphEdge.subject_id == node_id,
                GraphEdge.object_id == node_id,
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
