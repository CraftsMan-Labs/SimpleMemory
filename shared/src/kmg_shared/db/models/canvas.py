from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kmg_shared.db.models.base import Base, TimestampMixin


class WikiCanvas(TimestampMixin, Base):
    __tablename__ = "wiki_canvases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    title: Mapped[str] = mapped_column(Text)
    layout: Mapped[dict] = mapped_column(type_=JSONB, default=dict)
    meta_: Mapped[dict] = mapped_column("metadata", type_=JSONB, default=dict)

    items: Mapped[list[WikiCanvasItem]] = relationship(back_populates="canvas")
    edges: Mapped[list[WikiCanvasEdge]] = relationship(back_populates="canvas")


class WikiCanvasItem(TimestampMixin, Base):
    __tablename__ = "wiki_canvas_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    canvas_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_canvases.id"), index=True)
    item_type: Mapped[str] = mapped_column(Text)
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    width: Mapped[float] = mapped_column(Float)
    height: Mapped[float] = mapped_column(Float)
    style: Mapped[dict] = mapped_column(type_=JSONB, default=dict)

    canvas: Mapped[WikiCanvas] = relationship(back_populates="items")


class WikiCanvasEdge(TimestampMixin, Base):
    __tablename__ = "wiki_canvas_edges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    canvas_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_canvases.id"), index=True)
    from_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_canvas_items.id"), index=True)
    to_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wiki_canvas_items.id"), index=True)
    label: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    edge_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    style: Mapped[dict] = mapped_column(type_=JSONB, default=dict)

    canvas: Mapped[WikiCanvas] = relationship(back_populates="edges")
