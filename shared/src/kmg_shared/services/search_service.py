from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from kmg_shared.ports.embedding import EmbeddingProvider
from kmg_shared.ports.vector_db import ScoredResult, VectorDB


@dataclass
class SearchResultItem:
    id: uuid.UUID
    record_type: str
    score: float
    title: str | None
    slug: str | None
    snippet: str | None
    workspace_id: uuid.UUID
    metadata: dict[str, Any]


@dataclass
class SearchResult:
    query: str
    results: list[SearchResultItem]
    total_found: int


class SearchService:
    def __init__(
        self,
        embedding: EmbeddingProvider,
        vector_db: VectorDB,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._embedding = embedding
        self._vector_db = vector_db
        self._session_factory = session_factory

    async def search(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        query: str,
        *,
        scope: str = "current_project",
        record_types: list[str] | None = None,
        limit: int = 20,
    ) -> SearchResult:
        if record_types is None:
            record_types = ["wiki_page", "graph_node", "chunk", "fact"]

        query_vector = await self._embedding.embed_text(query)

        ws_filter = str(workspace_id) if scope == "current_project" else None
        scored_results: list[ScoredResult] = await self._vector_db.search(
            tenant_id=str(tenant_id),
            workspace_id=ws_filter,
            query_vector=query_vector,
            record_types=record_types,
            limit=limit,
        )

        items = await self._hydrate_results(scored_results, workspace_id)
        return SearchResult(query=query, results=items, total_found=len(items))

    async def _hydrate_results(
        self,
        scored: list[ScoredResult],
        workspace_id: uuid.UUID,
    ) -> list[SearchResultItem]:
        items: list[SearchResultItem] = []
        for result in scored:
            payload = result.payload
            items.append(
                SearchResultItem(
                    id=uuid.UUID(result.id),
                    record_type=payload.get("record_type", "unknown"),
                    score=result.score,
                    title=payload.get("title"),
                    slug=payload.get("slug"),
                    snippet=payload.get("snippet"),
                    workspace_id=uuid.UUID(
                        payload.get("workspace_id", str(workspace_id))
                    ),
                    metadata={
                        k: v
                        for k, v in payload.items()
                        if k not in (
                            "title", "slug", "snippet",
                            "record_type", "workspace_id",
                        )
                    },
                )
            )
        return items
