from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class VectorRecord:
    id: str
    vector: list[float]
    payload: dict


@dataclass
class ScoredResult:
    id: str
    score: float
    payload: dict


class VectorDB(Protocol):
    """Abstract vector database -- swap Qdrant/Pinecone/Weaviate/pgvector."""

    async def upsert(
        self,
        tenant_id: str,
        workspace_id: str,
        record_type: str,
        records: list[VectorRecord],
    ) -> int: ...

    async def search(
        self,
        tenant_id: str,
        workspace_id: str | None,
        query_vector: list[float],
        record_types: list[str],
        limit: int = 20,
        filters: dict | None = None,
    ) -> list[ScoredResult]: ...

    async def delete_by_record_ids(
        self,
        tenant_id: str,
        record_ids: list[str],
    ) -> int: ...

    async def ensure_collection(self, tenant_id: str, vector_size: int) -> None: ...
