from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.db.models.api_key import ApiKey
from kmg_shared.repositories.base_repo import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKey]):
    model = ApiKey

    async def create(
        self,
        tenant_id: uuid.UUID,
        key_hash: str,
        prefix: str,
        name: str,
        *,
        workspace_id: uuid.UUID | None = None,
        permissions: dict[str, Any] | None = None,
        expires_at: datetime | None = None,
    ) -> ApiKey:
        api_key = ApiKey(
            tenant_id=tenant_id,
            key_hash=key_hash,
            prefix=prefix,
            name=name,
            workspace_id=workspace_id,
            permissions=permissions or {},
            expires_at=expires_at,
        )
        self._session.add(api_key)
        await self._session.flush()
        return api_key

    async def get_by_prefix(self, prefix: str) -> ApiKey | None:
        stmt = select(ApiKey).where(ApiKey.prefix == prefix)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_key_hash(self, key_hash: str) -> ApiKey | None:
        stmt = select(ApiKey).where(ApiKey.key_hash == key_hash)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, api_key_id: uuid.UUID) -> None:
        stmt = update(ApiKey).where(ApiKey.id == api_key_id).values(status="revoked")
        await self._session.execute(stmt)

    async def list_for_tenant(self, tenant_id: uuid.UUID) -> list[ApiKey]:
        stmt = select(ApiKey).where(ApiKey.tenant_id == tenant_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
