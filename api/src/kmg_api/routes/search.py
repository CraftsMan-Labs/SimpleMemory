from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from kmg_api.dependencies import TenantId, WorkspaceId, get_search_service
from kmg_api.schemas.search import (
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SearchResponse,
)
from kmg_shared.services import SearchService

router = APIRouter(prefix="/v1", tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    search_service: Annotated[SearchService, Depends(get_search_service)],
) -> dict:
    result = await search_service.search(
        tenant_id,
        workspace_id,
        body.query,
        scope=body.scope,
        record_types=body.record_types,
        limit=body.limit,
    )
    return {
        "query": result.query,
        "results": [
            {
                "id": item.id,
                "record_type": item.record_type,
                "score": item.score,
                "title": item.title,
                "slug": item.slug,
                "snippet": item.snippet,
                "workspace_id": item.workspace_id,
                "metadata": item.metadata,
            }
            for item in result.results
        ],
        "answer": None,
        "citations": [],
        "total_found": result.total_found,
        "confidence": None,
        "follow_up_suggestions": [],
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    search_service: Annotated[SearchService, Depends(get_search_service)],
) -> dict:
    conversation_id = body.conversation_id or uuid.uuid4()

    result = await search_service.search(
        tenant_id, workspace_id, body.query, scope=body.scope, limit=5
    )

    context_snippets = [
        item.snippet or item.title or "" for item in result.results if item.snippet or item.title
    ]
    answer = (
        f"Based on {len(context_snippets)} relevant sources: "
        + "; ".join(context_snippets[:3])
        if context_snippets
        else "No relevant information found for your query."
    )

    return {
        "answer": answer,
        "citations": [
            {"id": str(item.id), "title": item.title, "score": item.score}
            for item in result.results[:5]
        ],
        "confidence": max((item.score for item in result.results), default=None),
        "conversation_id": conversation_id,
        "follow_up_suggestions": [],
    }
