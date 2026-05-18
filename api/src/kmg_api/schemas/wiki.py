from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class WikiPageResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    slug: str
    title: str
    page_type: str
    markdown: str
    summary: str | None
    freshness_status: str
    source_count: int
    chunk_count: int
    graph_node_count: int
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WikiPageListResponse(BaseModel):
    pages: list[WikiPageResponse]
    total: int


class UpdateWikiPageRequest(BaseModel):
    markdown: str | None = None
    summary: str | None = None
    title: str | None = None


class WikiLinkResponse(BaseModel):
    id: uuid.UUID
    from_wiki_page_id: uuid.UUID
    to_wiki_page_id: uuid.UUID
    link_text: str
    link_type: str
    confidence: float
    created_by: str
    status: str

    model_config = {"from_attributes": True}


class WikiBacklinkResponse(BaseModel):
    id: uuid.UUID
    wiki_page_id: uuid.UUID
    referring_wiki_page_id: uuid.UUID
    context_snippet: str | None

    model_config = {"from_attributes": True}


class WikiRevisionResponse(BaseModel):
    id: uuid.UUID
    wiki_page_id: uuid.UUID
    revision_number: int
    markdown: str
    author_type: str
    change_summary: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
