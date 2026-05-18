from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from kmg_api.dependencies import TenantId, WorkspaceId, get_wiki_service
from kmg_api.schemas.wiki import (
    UpdateWikiPageRequest,
    WikiBacklinkResponse,
    WikiEvidenceResponse,
    WikiPageListResponse,
    WikiPageResponse,
    WikiRevisionResponse,
)
from kmg_shared.services import WikiService

router = APIRouter(prefix="/v1/wiki", tags=["wiki"])


@router.get("/pages", response_model=WikiPageListResponse)
async def list_wiki_pages(
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    wiki_service: Annotated[WikiService, Depends(get_wiki_service)],
    q: Annotated[str | None, Query(description="Title/slug substring filter")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    pages, total = await wiki_service.list_pages(
        tenant_id, workspace_id, limit=limit, offset=offset, q=q
    )
    return {"pages": pages, "total": total}


@router.get("/pages/{page_id}", response_model=WikiPageResponse)
async def get_wiki_page(
    page_id: uuid.UUID,
    tenant_id: TenantId,
    wiki_service: Annotated[WikiService, Depends(get_wiki_service)],
) -> object:
    return await wiki_service.get_page(tenant_id, page_id)


@router.get("/pages/by-slug/{slug}", response_model=WikiPageResponse)
async def get_wiki_page_by_slug(
    slug: str,
    tenant_id: TenantId,
    workspace_id: WorkspaceId,
    wiki_service: Annotated[WikiService, Depends(get_wiki_service)],
) -> object:
    return await wiki_service.get_page_by_slug(tenant_id, workspace_id, slug)


@router.patch("/pages/{page_id}", response_model=WikiPageResponse)
async def update_wiki_page(
    page_id: uuid.UUID,
    body: UpdateWikiPageRequest,
    tenant_id: TenantId,
    wiki_service: Annotated[WikiService, Depends(get_wiki_service)],
) -> object:
    return await wiki_service.update_page(
        tenant_id, page_id, markdown=body.markdown, summary=body.summary, title=body.title
    )


@router.get("/pages/{page_id}/backlinks", response_model=list[WikiBacklinkResponse])
async def get_wiki_backlinks(
    page_id: uuid.UUID,
    tenant_id: TenantId,
    wiki_service: Annotated[WikiService, Depends(get_wiki_service)],
) -> list:
    return await wiki_service.get_backlinks(tenant_id, page_id)


@router.get("/pages/{page_id}/revisions", response_model=list[WikiRevisionResponse])
async def get_wiki_revisions(
    page_id: uuid.UUID,
    tenant_id: TenantId,
    wiki_service: Annotated[WikiService, Depends(get_wiki_service)],
) -> list:
    return await wiki_service.get_revisions(tenant_id, page_id)


@router.get("/pages/{page_id}/evidence", response_model=list[WikiEvidenceResponse])
async def get_wiki_evidence(
    page_id: uuid.UUID,
    tenant_id: TenantId,
    wiki_service: Annotated[WikiService, Depends(get_wiki_service)],
) -> list:
    return await wiki_service.get_evidence(tenant_id, page_id)
