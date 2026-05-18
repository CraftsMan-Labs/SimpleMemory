from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from kmg_shared.db.models.base import Base, TimestampMixin


class Fact(TimestampMixin, Base):
    __tablename__ = "facts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    canonical_text: Mapped[str] = mapped_column(Text)
    fact_type: Mapped[str] = mapped_column(Text)
    subject_graph_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("graph_nodes.id"), nullable=True
    )
    object_graph_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("graph_nodes.id"), nullable=True
    )
    source_wiki_page_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("wiki_pages.id"), nullable=True
    )
    confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(Text, default="active")
    source_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)


class FactEvidence(TimestampMixin, Base):
    __tablename__ = "fact_evidence"

    fact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facts.id"), primary_key=True)
    chunk_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chunks.id"), primary_key=True)
    evidence_role: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    quote: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DerivationEdge(TimestampMixin, Base):
    __tablename__ = "derivation_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    from_type: Mapped[str] = mapped_column(Text)
    from_id: Mapped[uuid.UUID] = mapped_column()
    to_type: Mapped[str] = mapped_column(Text)
    to_id: Mapped[uuid.UUID] = mapped_column()
    transform_name: Mapped[str] = mapped_column(Text)
    transform_version: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
