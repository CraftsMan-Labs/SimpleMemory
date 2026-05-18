from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    scope: str = Field(default="current_project", description="current_project | all_projects | shared_projects")
    record_types: list[str] = Field(default_factory=lambda: ["wiki_page", "graph_node", "chunk", "fact"])
    limit: int = Field(default=20, ge=1, le=100)


class SearchResultItem(BaseModel):
    id: uuid.UUID
    record_type: str
    score: float
    title: str | None = None
    slug: str | None = None
    snippet: str | None = None
    workspace_id: uuid.UUID
    metadata: dict = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    answer: str | None = None
    citations: list[dict] = Field(default_factory=list)
    total_found: int
    confidence: float | None = None
    follow_up_suggestions: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    scope: str = Field(default="current_project")
    conversation_id: uuid.UUID | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[dict] = Field(default_factory=list)
    confidence: float | None = None
    conversation_id: uuid.UUID
    follow_up_suggestions: list[str] = Field(default_factory=list)
