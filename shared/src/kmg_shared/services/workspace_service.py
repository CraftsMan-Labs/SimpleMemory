from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.workspace import Workspace
from kmg_shared.errors import ConflictError, NotFoundError


class WorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_workspace(
        self,
        tenant_id: uuid.UUID,
        *,
        name: str,
        slug: str,
        settings: dict[str, Any] | None = None,
    ) -> Workspace:
        existing = await self._session.execute(
            select(Workspace).where(
                Workspace.tenant_id == tenant_id,
                Workspace.slug == slug,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Workspace", f"slug '{slug}' already exists")

        workspace = Workspace(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            settings=settings or {},
        )
        self._session.add(workspace)
        await self._session.flush()
        return workspace

    async def get_workspace(
        self, tenant_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Workspace:
        result = await self._session.execute(
            select(Workspace).where(
                Workspace.id == workspace_id,
                Workspace.tenant_id == tenant_id,
            )
        )
        workspace = result.scalar_one_or_none()
        if not workspace:
            raise NotFoundError("Workspace", workspace_id)
        return workspace

    async def list_workspaces(self, tenant_id: uuid.UUID) -> list[Workspace]:
        result = await self._session.execute(
            select(Workspace).where(
                Workspace.tenant_id == tenant_id,
                Workspace.status == "active",
            )
        )
        return list(result.scalars().all())

    async def update_workspace(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        *,
        name: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Workspace:
        workspace = await self.get_workspace(tenant_id, workspace_id)

        if name is not None:
            workspace.name = name
        if settings is not None:
            workspace.settings = settings

        await self._session.flush()
        return workspace
