"""Initial KMG v3 schema.

Revision ID: 001_initial_v3
Revises:
Create Date: 2026-05-18
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_v3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.Text(), unique=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("plan", sa.Text(), nullable=False, server_default="free"),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "memberships",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "workspaces",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("settings", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "workspace_members",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("uri", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "source_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False, index=True),
        sa.Column("parser_version", sa.Text(), nullable=True),
        sa.Column("raw_object_key", sa.Text(), nullable=False),
        sa.Column("normalized_text_object_key", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "document_segments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False, index=True),
        sa.Column("source_version_id", sa.Uuid(), sa.ForeignKey("source_versions.id"), nullable=False, index=True),
        sa.Column("segment_type", sa.Text(), nullable=False),
        sa.Column("segment_key", sa.Text(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("text_hash", sa.Text(), nullable=True),
        sa.Column("semantic_hash", sa.Text(), nullable=True),
        sa.Column("stable_anchor", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chunks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False, index=True),
        sa.Column("source_version_id", sa.Uuid(), sa.ForeignKey("source_versions.id"), nullable=False, index=True),
        sa.Column("segment_id", sa.Uuid(), sa.ForeignKey("document_segments.id"), nullable=False, index=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.Text(), nullable=True),
        sa.Column("semantic_hash", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("superseded_by_chunk_id", sa.Uuid(), sa.ForeignKey("chunks.id"), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "graph_nodes",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("node_type", sa.Text(), nullable=False),
        sa.Column("canonical_name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("aliases", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("primary_wiki_page_id", sa.Uuid(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wiki_pages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("page_type", sa.Text(), nullable=False),
        sa.Column("markdown", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("owning_graph_node_id", sa.Uuid(), nullable=True),
        sa.Column("freshness_status", sa.Text(), nullable=False, server_default="fresh"),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("graph_node_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Deferred FK between wiki_pages and graph_nodes
    op.create_foreign_key(
        "fk_wiki_pages_owning_graph_node",
        "wiki_pages", "graph_nodes",
        ["owning_graph_node_id"], ["id"],
    )
    op.create_foreign_key(
        "fk_graph_nodes_primary_wiki_page",
        "graph_nodes", "wiki_pages",
        ["primary_wiki_page_id"], ["id"],
    )

    op.create_table(
        "wiki_revisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=False, index=True),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("markdown", sa.Text(), nullable=False),
        sa.Column("markdown_hash", sa.Text(), nullable=True),
        sa.Column("author_type", sa.Text(), nullable=False),
        sa.Column("author_user_id", sa.Uuid(), nullable=True),
        sa.Column("base_revision_id", sa.Uuid(), sa.ForeignKey("wiki_revisions.id"), nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wiki_evidence",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=False, index=True),
        sa.Column("chunk_id", sa.Uuid(), sa.ForeignKey("chunks.id"), nullable=False, index=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False, index=True),
        sa.Column("source_version_id", sa.Uuid(), sa.ForeignKey("source_versions.id"), nullable=False, index=True),
        sa.Column("evidence_role", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wiki_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("from_wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=False, index=True),
        sa.Column("to_wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=False, index=True),
        sa.Column("link_text", sa.Text(), nullable=False),
        sa.Column("link_type", sa.Text(), nullable=False),
        sa.Column("anchor", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_by", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wiki_backlinks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=False, index=True),
        sa.Column("referring_wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=False, index=True),
        sa.Column("wiki_link_id", sa.Uuid(), sa.ForeignKey("wiki_links.id"), nullable=False, index=True),
        sa.Column("context_snippet", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "graph_edges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("subject_type", sa.Text(), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("predicate", sa.Text(), nullable=False),
        sa.Column("object_type", sa.Text(), nullable=False),
        sa.Column("object_id", sa.Uuid(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("evidence_chunk_id", sa.Uuid(), sa.ForeignKey("chunks.id"), nullable=True),
        sa.Column("evidence_wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wiki_graph_links",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=False, index=True),
        sa.Column("graph_node_id", sa.Uuid(), sa.ForeignKey("graph_nodes.id"), nullable=False, index=True),
        sa.Column("link_type", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "facts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("canonical_text", sa.Text(), nullable=False),
        sa.Column("fact_type", sa.Text(), nullable=False),
        sa.Column("subject_graph_node_id", sa.Uuid(), sa.ForeignKey("graph_nodes.id"), nullable=True),
        sa.Column("object_graph_node_id", sa.Uuid(), sa.ForeignKey("graph_nodes.id"), nullable=True),
        sa.Column("source_wiki_page_id", sa.Uuid(), sa.ForeignKey("wiki_pages.id"), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("source_type", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "fact_evidence",
        sa.Column("fact_id", sa.Uuid(), sa.ForeignKey("facts.id"), primary_key=True),
        sa.Column("chunk_id", sa.Uuid(), sa.ForeignKey("chunks.id"), primary_key=True),
        sa.Column("evidence_role", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "derivation_edges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("from_type", sa.Text(), nullable=False),
        sa.Column("from_id", sa.Uuid(), nullable=False),
        sa.Column("to_type", sa.Text(), nullable=False),
        sa.Column("to_id", sa.Uuid(), nullable=False),
        sa.Column("transform_name", sa.Text(), nullable=False),
        sa.Column("transform_version", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wiki_canvases",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("layout", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wiki_canvas_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("canvas_id", sa.Uuid(), sa.ForeignKey("wiki_canvases.id"), nullable=False, index=True),
        sa.Column("item_type", sa.Text(), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=True),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("style", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wiki_canvas_edges",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("canvas_id", sa.Uuid(), sa.ForeignKey("wiki_canvases.id"), nullable=False, index=True),
        sa.Column("from_item_id", sa.Uuid(), sa.ForeignKey("wiki_canvas_items.id"), nullable=False, index=True),
        sa.Column("to_item_id", sa.Uuid(), sa.ForeignKey("wiki_canvas_items.id"), nullable=False, index=True),
        sa.Column("label", sa.Text(), nullable=True),
        sa.Column("edge_type", sa.Text(), nullable=True),
        sa.Column("style", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=False, index=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id"), nullable=False, index=True),
        sa.Column("source_version_id", sa.Uuid(), sa.ForeignKey("source_versions.id"), nullable=False, index=True),
        sa.Column("pipeline_id", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="queued"),
        sa.Column("stage", sa.Text(), nullable=True),
        sa.Column("progress", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("workspace_id", sa.Uuid(), sa.ForeignKey("workspaces.id"), nullable=True, index=True),
        sa.Column("key_hash", sa.Text(), unique=True, nullable=False),
        sa.Column("prefix", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("permissions", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("api_keys")
    op.drop_table("ingestion_jobs")
    op.drop_table("wiki_canvas_edges")
    op.drop_table("wiki_canvas_items")
    op.drop_table("wiki_canvases")
    op.drop_table("derivation_edges")
    op.drop_table("fact_evidence")
    op.drop_table("facts")
    op.drop_table("wiki_graph_links")
    op.drop_table("graph_edges")
    op.drop_table("wiki_backlinks")
    op.drop_table("wiki_links")
    op.drop_table("wiki_evidence")
    op.drop_table("wiki_revisions")
    op.drop_constraint("fk_graph_nodes_primary_wiki_page", "graph_nodes", type_="foreignkey")
    op.drop_constraint("fk_wiki_pages_owning_graph_node", "wiki_pages", type_="foreignkey")
    op.drop_table("wiki_pages")
    op.drop_table("graph_nodes")
    op.drop_table("chunks")
    op.drop_table("document_segments")
    op.drop_table("source_versions")
    op.drop_table("sources")
    op.drop_table("workspace_members")
    op.drop_table("workspaces")
    op.drop_table("memberships")
    op.drop_table("tenants")
    op.drop_table("users")
