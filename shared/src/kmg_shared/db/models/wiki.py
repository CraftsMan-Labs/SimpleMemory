from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kmg_shared.db.models.base import Base, TimestampMixin


class WikiPage(TimestampMixin, Base):
    __tablename__ = "wiki_pages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    slug: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    page_type: Mapped[str] = mapped_column(Text)
    markdown: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owning_graph_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("graph_nodes.id", use_alter=True), nullable=True
    )
    freshness_status: Mapped[str] = mapped_column(Text, default="fresh")
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    graph_node_count: Mapped[int] = mapped_column(Integer, default=0)
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)

    revisions: Mapped[list[WikiRevision]] = relationship(back_populates="wiki_page")
    evidence: Mapped[list[WikiEvidence]] = relationship(back_populates="wiki_page")
    outgoing_links: Mapped[list[WikiLink]] = relationship(
        back_populates="from_wiki_page", foreign_keys="WikiLink.from_wiki_page_id"
    )
    incoming_links: Mapped[list[WikiLink]] = relationship(
        back_populates="to_wiki_page", foreign_keys="WikiLink.to_wiki_page_id"
    )
    backlinks: Mapped[list[WikiBacklink]] = relationship(
        back_populates="wiki_page", foreign_keys="WikiBacklink.wiki_page_id"
    )


class WikiRevision(TimestampMixin, Base):
    __tablename__ = "wiki_revisions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    wiki_page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_pages.id"), index=True)
    revision_number: Mapped[int] = mapped_column(Integer)
    markdown: Mapped[str] = mapped_column(Text)
    markdown_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_type: Mapped[str] = mapped_column(Text)
    author_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)
    base_revision_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("wiki_revisions.id"), nullable=True
    )
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    wiki_page: Mapped[WikiPage] = relationship(back_populates="revisions")


class WikiEvidence(TimestampMixin, Base):
    __tablename__ = "wiki_evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    wiki_page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_pages.id"), index=True)
    chunk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chunks.id"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), index=True)
    source_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_versions.id"), index=True)
    evidence_role: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    quote: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)

    wiki_page: Mapped[WikiPage] = relationship(back_populates="evidence")


class WikiLink(TimestampMixin, Base):
    __tablename__ = "wiki_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    from_wiki_page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_pages.id"), index=True)
    to_wiki_page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_pages.id"), index=True)
    link_text: Mapped[str] = mapped_column(Text)
    link_type: Mapped[str] = mapped_column(Text)
    anchor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float)
    created_by: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="active")
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)

    from_wiki_page: Mapped[WikiPage] = relationship(
        back_populates="outgoing_links", foreign_keys=[from_wiki_page_id]
    )
    to_wiki_page: Mapped[WikiPage] = relationship(
        back_populates="incoming_links", foreign_keys=[to_wiki_page_id]
    )


class WikiBacklink(TimestampMixin, Base):
    __tablename__ = "wiki_backlinks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    wiki_page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_pages.id"), index=True)
    referring_wiki_page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_pages.id"), index=True)
    wiki_link_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_links.id"), index=True)
    context_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    wiki_page: Mapped[WikiPage] = relationship(
        back_populates="backlinks", foreign_keys=[wiki_page_id]
    )
