from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.wiki import (
    WikiBacklink,
    WikiEvidence,
    WikiLink,
    WikiPage,
    WikiRevision,
)
from kmg_shared.repositories.base_repo import BaseRepository


class WikiRepository(BaseRepository[WikiPage]):
    model = WikiPage

    async def create_page(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        slug: str,
        title: str,
        page_type: str,
        markdown: str,
        *,
        summary: str | None = None,
        owning_graph_node_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> WikiPage:
        page = WikiPage(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            slug=slug,
            title=title,
            page_type=page_type,
            markdown=markdown,
            summary=summary,
            owning_graph_node_id=owning_graph_node_id,
            metadata=metadata or {},
        )
        self._session.add(page)
        await self._session.flush()
        return page

    async def get_page_by_slug(self, workspace_id: uuid.UUID, slug: str) -> WikiPage | None:
        stmt = select(WikiPage).where(
            WikiPage.workspace_id == workspace_id,
            WikiPage.slug == slug,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_page(
        self,
        page_id: uuid.UUID,
        *,
        markdown: str | None = None,
        summary: str | None = None,
        freshness_status: str | None = None,
    ) -> WikiPage:
        values: dict[str, Any] = {}
        if markdown is not None:
            values["markdown"] = markdown
        if summary is not None:
            values["summary"] = summary
        if freshness_status is not None:
            values["freshness_status"] = freshness_status

        if values:
            stmt = update(WikiPage).where(WikiPage.id == page_id).values(**values)
            await self._session.execute(stmt)

        return await self.get_by_id_or_raise(page_id)

    async def create_revision(
        self,
        wiki_page_id: uuid.UUID,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        revision_number: int,
        markdown: str,
        author_type: str,
        *,
        markdown_hash: str | None = None,
        author_user_id: uuid.UUID | None = None,
        base_revision_id: uuid.UUID | None = None,
        change_summary: str | None = None,
    ) -> WikiRevision:
        revision = WikiRevision(
            wiki_page_id=wiki_page_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            revision_number=revision_number,
            markdown=markdown,
            author_type=author_type,
            markdown_hash=markdown_hash,
            author_user_id=author_user_id,
            base_revision_id=base_revision_id,
            change_summary=change_summary,
        )
        self._session.add(revision)
        await self._session.flush()
        return revision

    async def create_evidence_batch(self, records: list[dict[str, Any]]) -> list[WikiEvidence]:
        objects = [WikiEvidence(**data) for data in records]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def create_links_batch(self, links: list[dict[str, Any]]) -> list[WikiLink]:
        objects = [WikiLink(**data) for data in links]
        self._session.add_all(objects)
        await self._session.flush()
        return objects

    async def get_backlinks(self, wiki_page_id: uuid.UUID) -> list[WikiBacklink]:
        stmt = select(WikiBacklink).where(WikiBacklink.wiki_page_id == wiki_page_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_backlinks_batch(self, backlinks: list[dict[str, Any]]) -> list[WikiBacklink]:
        objects = [WikiBacklink(**data) for data in backlinks]
        self._session.add_all(objects)
        await self._session.flush()
        return objects
