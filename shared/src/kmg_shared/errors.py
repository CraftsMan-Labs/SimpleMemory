from __future__ import annotations

import uuid


class KmgError(Exception):
    """Base for all KMG errors."""


class NotFoundError(KmgError):
    """Entity not found (404)."""

    def __init__(self, entity: str, identifier: str | uuid.UUID) -> None:
        self.entity = entity
        self.identifier = str(identifier)
        super().__init__(f"{entity} '{self.identifier}' not found")


class PermissionDeniedError(KmgError):
    """Tenant/workspace access denied (403)."""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message)


class ValidationError(KmgError):
    """Input validation failed (422)."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)


class ConflictError(KmgError):
    """Resource conflict (409) -- e.g. duplicate slug."""

    def __init__(self, entity: str, message: str) -> None:
        self.entity = entity
        super().__init__(f"{entity} conflict: {message}")


class IngestionError(KmgError):
    """Pipeline processing failure (retryable or terminal)."""

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


class SourceUploadNotFoundError(KmgError):
    """Presigned upload object not found in storage."""

    def __init__(self, source_id: uuid.UUID, version_id: uuid.UUID) -> None:
        self.source_id = source_id
        self.version_id = version_id
        super().__init__(
            f"Upload not found for source {source_id}, version {version_id}. "
            "The presigned upload may not have completed."
        )


class AuthenticationError(KmgError):
    """Authentication failed (401)."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message)


class RateLimitError(KmgError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded", *, retry_after: int | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after
