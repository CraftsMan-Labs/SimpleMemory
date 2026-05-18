from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.base import Base
from kmg_shared.errors import NotFoundError

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: uuid.UUID) -> T | None:
        return await self._session.get(self.model, id)

    async def get_by_id_or_raise(self, id: uuid.UUID) -> T:
        result = await self.get_by_id(id)
        if result is None:
            raise NotFoundError(self.model.__name__, id)
        return result

    async def list_by_workspace(
        self,
        tenant_id: uuid.UUID,
        workspace_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[T]:
        stmt = (
            select(self.model)
            .where(
                self.model.tenant_id == tenant_id,  # type: ignore[attr-defined]
                self.model.workspace_id == workspace_id,  # type: ignore[attr-defined]
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_workspace(self, tenant_id: uuid.UUID, workspace_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(
                self.model.tenant_id == tenant_id,  # type: ignore[attr-defined]
                self.model.workspace_id == workspace_id,  # type: ignore[attr-defined]
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
