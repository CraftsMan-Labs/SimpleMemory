from __future__ import annotations

import uuid

from fastapi import APIRouter

from kmg_api.dependencies import DbSession, TenantId
from kmg_api.schemas.chunk import ChunkResponse
from kmg_shared.errors import NotFoundError
from kmg_shared.repositories.chunk_repo import ChunkRepository

router = APIRouter(prefix="/v1/chunks", tags=["chunks"])


@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: uuid.UUID,
    tenant_id: TenantId,
    session: DbSession,
) -> object:
    repo = ChunkRepository(session)
    chunk = await repo.get_by_id(chunk_id)
    if chunk is None or chunk.tenant_id != tenant_id:
        raise NotFoundError("Chunk", chunk_id)
    return chunk
