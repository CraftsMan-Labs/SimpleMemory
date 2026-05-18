"""Type definitions for workflow handlers."""
from __future__ import annotations

from typing import Any, TypedDict


class WorkflowContext(TypedDict, total=False):
    """Context dict passed by SimpleAgents to each handler."""
    tenant_id: str
    workspace_id: str
    job_id: str
    pipeline_id: str


class ParseSourcePayload(TypedDict):
    tenant_id: str
    workspace_id: str
    source_id: str
    source_version_id: str
    source_type: str


class SegmentPayload(TypedDict):
    tenant_id: str
    workspace_id: str
    source_id: str
    source_version_id: str
    raw_text: str


class CreateChunksPayload(TypedDict):
    tenant_id: str
    workspace_id: str
    source_id: str
    source_version_id: str
    segment_ids: list[str]


class EmbedChunksPayload(TypedDict):
    tenant_id: str
    workspace_id: str
    chunk_ids: list[str]


class DeduplicateNodesPayload(TypedDict):
    workspace_id: str
    entities: list[dict[str, Any]]


class PersistGraphPayload(TypedDict):
    tenant_id: str
    workspace_id: str
    source_id: str
    node_proposals: list[dict[str, Any]]
    relations: list[dict[str, Any]]
    wiki_page_ids: list[str]


class EmbedGraphNodesPayload(TypedDict):
    tenant_id: str
    workspace_id: str
    node_ids: list[str]


class PersistWikiPayload(TypedDict):
    tenant_id: str
    workspace_id: str
    source_id: str
    source_version_id: str
    wiki_pages: list[dict[str, Any]]
    wiki_links: list[dict[str, Any]]


class EmbedWikiPayload(TypedDict):
    tenant_id: str
    workspace_id: str
    wiki_page_ids: list[str]


class LoadCanvasItemsPayload(TypedDict):
    canvas_id: str


class ApplyLayoutPayload(TypedDict):
    canvas_id: str
    groups: list[dict[str, Any]]
    suggested_edges: list[dict[str, Any]]


class VectorSearchPayload(TypedDict):
    tenant_id: str
    workspace_id: str
    refined_query: str
    record_types: list[str]
    limit: int
    intent: str


class HydrateResultsPayload(TypedDict):
    results: list[dict[str, Any]]
