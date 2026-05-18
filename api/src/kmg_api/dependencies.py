"""FastAPI dependency injection providers."""
from __future__ import annotations

import os
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from kmg_shared.auth.api_keys import hash_api_key
from kmg_shared.auth.scoping import RequestScope, require_workspace_access
from kmg_shared.auth.tokens import decode_token
from kmg_shared.db.session import get_session_factory
from kmg_shared.errors import AuthenticationError, ValidationError
from kmg_shared.infra.registry import get_embedding, get_queue, get_storage, get_vector_db
from kmg_shared.repositories import (
    ApiKeyRepository,
    CanvasRepository,
    GraphRepository,
    JobRepository,
    SourceRepository,
    WikiRepository,
)
from kmg_shared.services import (
    CanvasService,
    GraphService,
    SearchService,
    SourceService,
    WikiService,
    WorkspaceService,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def _is_production() -> bool:
    return os.environ.get("KMG_ENV", "development").lower() == "production"


async def get_request_scope(
    authorization: Annotated[str | None, Header()] = None,
    x_tenant_id: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_db_session),
) -> RequestScope:
    """Extract and validate auth from the Authorization header.

    Supports JWT (Bearer eyJ...), API keys (Bearer km_...),
    and dev bypass via X-Tenant-ID header in non-production.
    """
    # Dev/test bypass: allow X-Tenant-ID header in non-production
    if x_tenant_id and not _is_production():
        try:
            tenant_uuid = uuid.UUID(x_tenant_id)
        except ValueError as e:
            raise ValidationError("Invalid UUID format", field="x_tenant_id") from e
        return RequestScope(
            tenant_id=tenant_uuid,
            workspace_id=None,
            user_id=None,
            auth_type="dev_bypass",
            scopes=["read", "write", "admin"],
        )

    if not authorization:
        raise AuthenticationError("Authorization header required")

    token = authorization.removeprefix("Bearer ").strip()

    if token.startswith("km_"):
        key_hash = hash_api_key(token)
        api_key_repo = ApiKeyRepository(session)
        api_key = await api_key_repo.get_by_key_hash(key_hash)
        if api_key is None:
            raise AuthenticationError("Invalid API key")
        if api_key.status != "active":
            raise AuthenticationError("API key is revoked or inactive")

        scopes = api_key.permissions.get("scopes", ["read", "write"])
        return RequestScope(
            tenant_id=api_key.tenant_id,
            workspace_id=api_key.workspace_id,
            user_id=None,
            auth_type="api_key",
            scopes=scopes,
        )
    else:
        payload = decode_token(token)
        return RequestScope(
            tenant_id=payload.tenant_id,
            workspace_id=None,
            user_id=payload.user_id,
            auth_type="jwt",
            scopes=["read", "write"],
        )


async def get_tenant_id(
    scope: Annotated[RequestScope, Depends(get_request_scope)],
) -> uuid.UUID:
    return scope.tenant_id


async def get_workspace_id(
    scope: Annotated[RequestScope, Depends(get_request_scope)],
    x_workspace_id: Annotated[str, Header()],
) -> uuid.UUID:
    try:
        workspace_id = uuid.UUID(x_workspace_id)
    except ValueError as e:
        raise ValidationError("Invalid UUID format", field="x_workspace_id") from e
    require_workspace_access(scope, workspace_id)
    return workspace_id


DbSession = Annotated[AsyncSession, Depends(get_db_session)]
TenantId = Annotated[uuid.UUID, Depends(get_tenant_id)]
WorkspaceId = Annotated[uuid.UUID, Depends(get_workspace_id)]


# --- Service providers ---


async def get_source_service(session: DbSession) -> SourceService:
    return SourceService(
        source_repo=SourceRepository(session),
        job_repo=JobRepository(session),
        storage=get_storage(),
        queue=get_queue(),
    )


async def get_workspace_service(session: DbSession) -> WorkspaceService:
    return WorkspaceService(session)


async def get_wiki_service(session: DbSession) -> WikiService:
    return WikiService(wiki_repo=WikiRepository(session))


async def get_graph_service(session: DbSession) -> GraphService:
    return GraphService(graph_repo=GraphRepository(session))


async def get_search_service() -> SearchService:
    session_factory = get_session_factory()
    return SearchService(
        embedding=get_embedding(),
        vector_db=get_vector_db(),
        session_factory=session_factory,
    )


async def get_canvas_service(session: DbSession) -> CanvasService:
    return CanvasService(canvas_repo=CanvasRepository(session))
