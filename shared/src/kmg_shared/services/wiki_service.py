from __future__ import annotations

import uuid

from kmg_shared.db.models.wiki import WikiBacklink, WikiPage, WikiRevision
from kmg_shared.errors import NotFoundError
from kmg_shared.repositories.wiki_repo import WikiRepository


class WikiService:
    def __init__(self, wiki_repo: WikiRepository) -> None:
        self._wiki_repo = wiki_repo

    async def get_page(
        self, tenant_id: uuid.UUID, page_id: uuid.UUID
    ) -> WikiPage:
        page = await self._wiki_repo.get_by_id(page_id)
        if page is None or page.tenant_id != tenant_id:
            raise NotFoundError("WikiPage", page_id)
        return page

    async def get_page_by_slug(
        self, tenant_id: uuid.UUID, workspace_id: uuid.UUID, slug: str
    ) -> WikiPage:
        page = await self._wiki_repo.get_page_by_slug(workspace_id, slug)
        if page is None or page.tenant_id != tenant_id:
            raise NotFoundError("WikiPage", slug)
        return page

    async def list_pages(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[WikiPage], int]:
        pages = await self._wiki_repo.list_by_workspace(
            tenant_id, workspace_id, limit=limit, offset=offset
        )
        total = await self._wiki_repo.count_by_workspace(
            tenant_id, workspace_id
        )
        return pages, total

    async def update_page(
        self,
        tenant_id: uuid.UUID,
        page_id: uuid.UUID,
        *,
        markdown: str | None = None,
        summary: str | None = None,
        title: str | None = None,
    ) -> WikiPage:
        page = await self.get_page(tenant_id, page_id)

        update_kwargs: dict = {}
        if markdown is not None:
            update_kwargs["markdown"] = markdown
        if summary is not None:
            update_kwargs["summary"] = summary

        if update_kwargs:
            page = await self._wiki_repo.update_page(page_id, **update_kwargs)

        if title is not None:
            page.title = title  # type: ignore[assignment]

        return page

    async def get_backlinks(
        self, tenant_id: uuid.UUID, page_id: uuid.UUID
    ) -> list[WikiBacklink]:
        await self.get_page(tenant_id, page_id)
        return await self._wiki_repo.get_backlinks(page_id)

    async def get_revisions(
        self, tenant_id: uuid.UUID, page_id: uuid.UUID
    ) -> list[WikiRevision]:
        await self.get_page(tenant_id, page_id)
        from sqlalchemy import select
        from kmg_shared.db.models.wiki import WikiRevision as WR

        stmt = (
            select(WR)
            .where(WR.wiki_page_id == page_id, WR.tenant_id == tenant_id)
            .order_by(WR.revision_number.desc())
        )
        result = await self._wiki_repo._session.execute(stmt)
        return list(result.scalars().all())
