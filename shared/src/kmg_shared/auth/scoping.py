from __future__ import annotations

import uuid
from dataclasses import dataclass

from kmg_shared.errors import PermissionDeniedError


@dataclass
class RequestScope:
    """Resolved auth context for a request."""
    tenant_id: uuid.UUID
    workspace_id: uuid.UUID | None
    user_id: uuid.UUID | None
    auth_type: str  # "jwt" | "api_key"
    scopes: list[str]


def require_workspace_access(scope: RequestScope, workspace_id: uuid.UUID) -> None:
    """Verify the request scope has access to the given workspace."""
    if scope.workspace_id is not None and scope.workspace_id != workspace_id:
        raise PermissionDeniedError(
            f"API key is scoped to workspace {scope.workspace_id}, "
            f"cannot access workspace {workspace_id}"
        )


def require_scope(scope: RequestScope, required: str) -> None:
    """Verify the request has the required permission scope."""
    if required not in scope.scopes and "admin" not in scope.scopes:
        raise PermissionDeniedError(f"Missing required scope: {required}")


def require_tenant_match(scope: RequestScope, tenant_id: uuid.UUID) -> None:
    """Verify tenant_id matches the authenticated tenant."""
    if scope.tenant_id != tenant_id:
        raise PermissionDeniedError("Tenant mismatch")
