"""Verify all SQLAlchemy models are importable and correctly configured."""
from __future__ import annotations

import pytest

from kmg_shared.db.models import (
    ApiKey, Base, Chunk, DerivationEdge, DocumentSegment,
    Fact, FactEvidence, GraphEdge, GraphNode,
    IngestionJob, Membership, Source, SourceVersion,
    Tenant, User, WikiBacklink, WikiCanvas, WikiCanvasEdge,
    WikiCanvasItem, WikiEvidence, WikiGraphLink, WikiLink,
    WikiPage, WikiRevision, Workspace, WorkspaceMember,
)


EXPECTED_TABLES = {
    "users", "tenants", "memberships",
    "workspaces", "workspace_members",
    "sources", "source_versions",
    "document_segments", "chunks",
    "wiki_pages", "wiki_revisions", "wiki_evidence", "wiki_links", "wiki_backlinks",
    "graph_nodes", "graph_edges", "wiki_graph_links",
    "facts", "fact_evidence", "derivation_edges",
    "wiki_canvases", "wiki_canvas_items", "wiki_canvas_edges",
    "ingestion_jobs",
    "api_keys",
}


def test_all_tables_registered():
    """All expected tables should be in Base.metadata."""
    registered = set(Base.metadata.tables.keys())
    missing = EXPECTED_TABLES - registered
    assert not missing, f"Missing tables: {missing}"


@pytest.mark.parametrize("model_cls", [
    User, Tenant, Membership, Workspace, WorkspaceMember,
    Source, SourceVersion, DocumentSegment, Chunk,
    WikiPage, WikiRevision, WikiEvidence, WikiLink, WikiBacklink,
    GraphNode, GraphEdge, WikiGraphLink,
    Fact, DerivationEdge,
    WikiCanvas, WikiCanvasItem, WikiCanvasEdge,
    IngestionJob, ApiKey,
])
def test_model_has_timestamp_columns(model_cls):
    """All models (except FactEvidence) should have created_at and updated_at."""
    columns = {c.name for c in model_cls.__table__.columns}
    assert "created_at" in columns, f"{model_cls.__name__} missing created_at"
    assert "updated_at" in columns, f"{model_cls.__name__} missing updated_at"


def test_fact_evidence_composite_pk():
    """FactEvidence should have composite PK on fact_id + chunk_id."""
    pk_cols = {c.name for c in FactEvidence.__table__.primary_key.columns}
    assert "fact_id" in pk_cols
    assert "chunk_id" in pk_cols
