from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kmg_shared.db.models.base import Base, TimestampMixin


class DocumentSegment(TimestampMixin, Base):
    __tablename__ = "document_segments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), index=True)
    source_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_versions.id"), index=True)
    segment_type: Mapped[str] = mapped_column(Text)
    segment_key: Mapped[str] = mapped_column(Text)
    ordinal: Mapped[int] = mapped_column(Integer)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    text_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    semantic_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stable_anchor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, default="active")
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)

    chunks: Mapped[list[Chunk]] = relationship(back_populates="segment")


class Chunk(TimestampMixin, Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"), index=True)
    source_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_versions.id"), index=True)
    segment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document_segments.id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    semantic_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, default="active")
    superseded_by_chunk_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("chunks.id"), nullable=True
    )
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)

    segment: Mapped[DocumentSegment] = relationship(back_populates="chunks")
