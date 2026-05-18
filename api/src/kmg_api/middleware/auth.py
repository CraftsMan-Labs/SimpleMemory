from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header

from kmg_shared.auth.api_keys import hash_api_key
from kmg_shared.auth.scoping import RequestScope, require_workspace_access
from kmg_shared.auth.tokens import decode_token
from kmg_shared.errors import AuthenticationError


async def get_request_scope(
    authorization: Annotated[str, Header()],
) -> RequestScope:
    """Extract and validate auth from the Authorization header.

    Supports both JWT tokens and API keys.
    JWT: Bearer eyJ...
    API Key: Bearer km_...

    Note: Full implementation with DB lookup is in dependencies.py.
    This module provides the base logic for token decoding.
    """
    if not authorization:
        raise AuthenticationError("Authorization header required")

    token = authorization.removeprefix("Bearer ").strip()

    if token.startswith("km_"):
        key_hash = hash_api_key(token)
        raise AuthenticationError(
            "API key validation requires DB session -- use dependencies.get_request_scope()"
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


async def get_tenant_id(scope: Annotated[RequestScope, Depends(get_request_scope)]) -> uuid.UUID:
    return scope.tenant_id


async def get_workspace_id(
    scope: Annotated[RequestScope, Depends(get_request_scope)],
    x_workspace_id: Annotated[str, Header()],
) -> uuid.UUID:
    workspace_id = uuid.UUID(x_workspace_id)
    require_workspace_access(scope, workspace_id)
    return workspace_id
