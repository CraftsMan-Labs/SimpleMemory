from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.fact import DerivationEdge, Fact, FactEvidence
from kmg_shared.repositories.base_repo import BaseRepository


class FactRepository(BaseRepository[Fact]):
    model = Fact

    async def create_fact(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        canonical_text: str,
        fact_type: str,
        *,
        subject_graph_node_id: uuid.UUID | None = None,
        object_graph_node_id: uuid.UUID | None = None,
        source_wiki_page_id: uuid.UUID | None = None,
        confidence: float = 1.0,
        source_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Fact:
        fact = Fact(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            canonical_text=canonical_text,
            fact_type=fact_type,
            subject_graph_node_id=subject_graph_node_id,
            object_graph_node_id=object_graph_node_id,
            source_wiki_page_id=source_wiki_page_id,
            confidence=confidence,
            source_type=source_type,
            metadata=metadata or {},
        )
        self._session.add(fact)
        await self._session.flush()
        return fact

    async def create_facts_batch(self, facts: list[dict[str, Any]]) -> list[Fact]:
        objects = [Fact(**data) for data in facts]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def create_evidence_batch(self, evidence: list[dict[str, Any]]) -> list[FactEvidence]:
        objects = [FactEvidence(**data) for data in evidence]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def create_derivation_edges_batch(
        self, edges: list[dict[str, Any]]
    ) -> list[DerivationEdge]:
        objects = [DerivationEdge(**data) for data in edges]
        self._session.add_all(objects)
        await self._session.flush()
        return objects
