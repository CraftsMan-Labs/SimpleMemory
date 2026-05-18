from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ARRAY, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from kmg_shared.db.models.base import Base, TimestampMixin


class GraphNode(TimestampMixin, Base):
    __tablename__ = "graph_nodes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    node_type: Mapped[str] = mapped_column(Text)
    canonical_name: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    aliases: Mapped[list[str]] = mapped_column(type_=ARRAY(Text), default=list)
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(Text, default="active")
    primary_wiki_page_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("wiki_pages.id", use_alter=True), nullable=True
    )
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)


class GraphEdge(TimestampMixin, Base):
    __tablename__ = "graph_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    subject_type: Mapped[str] = mapped_column(Text)
    subject_id: Mapped[uuid.UUID] = mapped_column()
    predicate: Mapped[str] = mapped_column(Text)
    object_type: Mapped[str] = mapped_column(Text)
    object_id: Mapped[uuid.UUID] = mapped_column()
    confidence: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    evidence_chunk_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("chunks.id"), nullable=True
    )
    evidence_wiki_page_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("wiki_pages.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(Text, default="active")
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)


class WikiGraphLink(TimestampMixin, Base):
    __tablename__ = "wiki_graph_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    wiki_page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_pages.id"), index=True)
    graph_node_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("graph_nodes.id"), index=True)
    link_type: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(Text, default="active")
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)
