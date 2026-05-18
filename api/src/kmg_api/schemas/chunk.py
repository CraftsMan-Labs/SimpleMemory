from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ChunkResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID
    source_id: uuid.UUID
    source_version_id: uuid.UUID
    segment_id: uuid.UUID
    chunk_index: int
    text: str
    content_hash: str | None
    status: str
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
