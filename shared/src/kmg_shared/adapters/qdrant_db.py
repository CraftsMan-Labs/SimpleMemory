from __future__ import annotations

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from kmg_shared.ports.vector_db import ScoredResult, VectorRecord
from kmg_shared.resilience import retry_transient


class QdrantVectorDB:
    """VectorDB implementation backed by Qdrant."""

    def __init__(
        self,
        url: str,
        collection_prefix: str = "tenant",
        api_key: str | None = None,
    ) -> None:
        self._client = AsyncQdrantClient(url=url, api_key=api_key)
        self._prefix = collection_prefix

    def _collection_name(self, tenant_id: str) -> str:
        return f"{self._prefix}_{tenant_id}_knowledge_v1"

    @retry_transient
    async def upsert(
        self,
        tenant_id: str,
        workspace_id: str,
        record_type: str,
        records: list[VectorRecord],
    ) -> int:
        collection = self._collection_name(tenant_id)
        points = [
            PointStruct(
                id=rec.id,
                vector=rec.vector,
                payload={
                    **rec.payload,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "record_type": record_type,
                    "status": "active",
                },
            )
            for rec in records
        ]
        await self._client.upsert(collection_name=collection, points=points)
        return len(points)

    @retry_transient
    async def search(
        self,
        tenant_id: str,
        workspace_id: str | None,
        query_vector: list[float],
        record_types: list[str],
        limit: int = 20,
        filters: dict | None = None,
    ) -> list[ScoredResult]:
        collection = self._collection_name(tenant_id)

        must_conditions = [
            FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id)),
            FieldCondition(key="status", match=MatchValue(value="active")),
        ]

        if workspace_id is not None:
            must_conditions.append(
                FieldCondition(key="workspace_id", match=MatchValue(value=workspace_id))
            )

        if record_types:
            for rt in record_types:
                must_conditions.append(
                    FieldCondition(key="record_type", match=MatchValue(value=rt))
                )

        if filters:
            for key, value in filters.items():
                must_conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )

        results = await self._client.search(
            collection_name=collection,
            query_vector=query_vector,
            query_filter=Filter(must=must_conditions),
            limit=limit,
        )

        return [
            ScoredResult(id=str(hit.id), score=hit.score, payload=hit.payload or {})
            for hit in results
        ]

    async def delete_by_record_ids(
        self,
        tenant_id: str,
        record_ids: list[str],
    ) -> int:
        collection = self._collection_name(tenant_id)
        await self._client.delete(
            collection_name=collection,
            points_selector=record_ids,
        )
        return len(record_ids)

    @retry_transient
    async def ensure_collection(self, tenant_id: str, vector_size: int) -> None:
        collection = self._collection_name(tenant_id)
        collections = await self._client.get_collections()
        existing = {c.name for c in collections.collections}

        if collection not in existing:
            await self._client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
